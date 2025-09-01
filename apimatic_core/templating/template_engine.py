from typing import List, Optional, Callable, Union, Tuple
from apimatic_core_interfaces.http.request import Request
from apimatic_core.templating.template_resolver import ExprResolver, MethodResolver, UrlResolver, PathResolver, HeaderResolver, \
    QueryResolver, JsonBodyPointerResolver


# ======================================================
# TemplateEngine for compiling and rendering message templates
# ======================================================
class TemplateEngine:
    """
    TemplateEngine parses and compiles message templates used for signing/verifying.

    It supports literal text, `{raw_body}`, and runtime expressions wrapped in `{$...}`:
      - {$method} -> HTTP method
      - {$url} -> Full URL
      - {$request.path} -> Path component
      - {$request.header.<HeaderName>} -> Header value
      - {$request.query.<ParamName>} -> Query parameter value
      - {$request.body#/pointer/path} -> Value extracted from JSON body by pointer

    Workflow:
        1. Compile the template once into a plan of callables.
        2. Render that plan with any Request to produce the message bytes.

    Example:
        engine = TemplateEngine()
        plan = engine.compile("{$method}:{$url}:{raw_body}")
        message_bytes = engine.render(plan, request)
    """

    def __init__(self, resolvers: Optional[List[ExprResolver]] = None) -> None:
        """
        Initialize a TemplateEngine.

        Args:
            resolvers: Optional list of custom resolvers; defaults to all built-in resolvers.
        """
        self._resolvers: List[ExprResolver] = resolvers or [
            MethodResolver(),
            UrlResolver(),
            PathResolver(),
            HeaderResolver(),
            QueryResolver(),
            JsonBodyPointerResolver(),
        ]

    def compile(self, template: str) -> List[Callable[[Request], bytes]]:
        """
        Compile a template into a list of callables, each resolving part of the message.

        Args:
            template: Template string containing literals, `{raw_body}`, and/or `{$...}` expressions.

        Returns:
            List of callables; pass a Request to each to get the final message bytes.
        """
        tokens = self.__tokenize(template)
        plan: List[Callable[[Request], bytes]] = []
        for kind, payload in tokens:
            if kind == "literal":
                data: bytes = payload  # type: ignore[assignment]
                plan.append(lambda _r, _data=data: _data)
            elif kind == "raw":
                plan.append(lambda r: self.__raw_body_bytes(r))
            else:  # kind == "expr"
                expr: str = payload  # type: ignore[assignment]
                plan.append(self.__compile_expr(expr))
        return plan

    def __compile_expr(self, expr: str) -> Callable[[Request], bytes]:
        """
        Locate the resolver for an expression and compile it to a callable.

        Args:
            expr: The raw expression text, e.g., "request.header.X-Signature".

        Returns:
            Callable that takes a Request and returns the resolved bytes.
        """
        for res in self._resolvers:
            if res.matches(expr):
                return res.compile(expr)
        # Unknown expressions safely resolve to empty
        return lambda _r: b""

    @staticmethod
    def render(plan: List[Callable[[Request], bytes]], request: Request) -> bytes:
        """
        Render a compiled plan into the final message bytes for signing.

        Args:
            plan: The compiled list of callables from `compile`.
            request: The Request instance to extract values from.

        Returns:
            Byte string representing the message to sign or verify.
        """
        return b"".join(fn(request) for fn in plan)

    # ==================================================
    # Private helpers (internal use only)
    # ==================================================

    @staticmethod
    def __raw_body_bytes(req: Request) -> bytes:
        """
        Safely return the raw request body as bytes, falling back to encoded body text.
        """
        raw = getattr(req, "raw_body", None)
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw)
        body = getattr(req, "body", None)
        return (body or "").encode("utf-8")

    # inside class TemplateEngine
    @staticmethod
    def __tokenize(template: str) -> List[Tuple[str, Union[bytes, str]]]:
        """
        Tokenize in one pass using a simple state machine.
        Produces:
          - ("literal", bytes)
          - ("raw", "")
          - ("expr", "request.header.X-Foo")
        """
        if not isinstance(template, str) or not template:
            raise ValueError("message_template must be a non-empty string.")

        LIT, RAW_CANDIDATE, EXPR = 0, 1, 2
        state = LIT
        out: List[Tuple[str, Union[bytes, str]]] = []
        buf: List[str] = []
        expr: List[str] = []

        i = 0
        s = template
        n = len(s)
        rb = "{raw_body}"
        rbl = len(rb)

        def flush_lit():
            if buf:
                out.append(("literal", "".join(buf).encode("utf-8")))
                buf.clear()

        def validate_expr(text: str):
            e = text.strip()
            if not e:
                raise ValueError("Empty runtime expression '{$ }' in message_template.")
            if "{" in e or "}" in e:
                raise ValueError("Runtime expression must not contain '{' or '}'.")
            if e.startswith("request.header."):
                if not e[len("request.header."):]:
                    raise ValueError("Header expression must specify a header name.")
            elif e.startswith("request.query."):
                if not e[len("request.query."):]:
                    raise ValueError("Query expression must specify a parameter name.")
            elif e.startswith("request.body#"):
                ptr = e[len("request.body#"):]
                if not ptr or not ptr.startswith("/"):
                    raise ValueError("JSON Pointer expression must start with '/'.")
            # unknown expressions are allowed; resolved to empty later

        while i < n:
            if state == LIT:
                # raw_body takes precedence
                if s.startswith(rb, i):
                    flush_lit()
                    out.append(("raw", ""))
                    i += rbl
                    continue
                # expression start
                if s.startswith("{$", i):
                    flush_lit()
                    i += 2
                    state = EXPR
                    expr.clear()
                    continue
                # keep literal char
                buf.append(s[i])
                i += 1
            elif state == EXPR:
                if i >= n:
                    # hit EOF without closing brace
                    raise ValueError("Unclosed '{$' in message_template.")
                ch = s[i]
                if ch == "}":
                    text = "".join(expr)
                    validate_expr(text)
                    out.append(("expr", text.strip()))
                    expr.clear()
                    state = LIT
                    i += 1
                else:
                    # Forbid nested braces *inside* an expression
                    if ch == "{" or ch == "}":
                        raise ValueError("Runtime expression must not contain '{' or '}'.")
                    expr.append(ch)
                    i += 1

        if state == EXPR:
            raise ValueError("Unclosed '{$' in message_template.")

        flush_lit()
        return out
