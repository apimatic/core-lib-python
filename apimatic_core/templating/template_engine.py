from typing import List, Optional, Callable, Union
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

    @staticmethod
    def __tokenize(template: str) -> List[tuple[str, Union[bytes, str]]]:
        """
        Parse a template string into tokens of types:
            - literal: static text
            - raw: {raw_body}
            - expr: {$...}

        Args:
            template: Template string.

        Returns:
            List of tuples (kind, value):
                - ("literal", bytes)
                - ("raw", "")
                - ("expr", "expression text")
        """
        if not isinstance(template, str) or not template:
            raise ValueError("message_template must be a non-empty string.")
        out: List[tuple[str, Union[bytes, str]]] = []
        i, s = 0, template
        rb, rblen = "{raw_body}", len("{raw_body}")
        while i < len(s):
            if s.startswith(rb, i):
                out.append(("raw", ""))
                i += rblen
                continue
            if s.startswith("{$", i):
                j = s.find("}", i + 2)
                if j == -1:
                    raise ValueError("Unclosed '{$' in message_template.")
                expr = s[i + 2 : j].strip()
                if not expr:
                    raise ValueError("Empty runtime expression '{$ }' in message_template.")
                out.append(("expr", expr))
                i = j + 1
                continue
            j1, j2 = s.find(rb, i), s.find("{$", i)
            next_pos = min([p for p in (j1, j2) if p != -1], default=-1)
            if next_pos == -1:
                out.append(("literal", s[i:].encode("utf-8")))
                break
            out.append(("literal", s[i:next_pos].encode("utf-8")))
            i = next_pos
        return out