from typing import Callable, Optional, Union, Mapping, Iterable, Dict, List

from apimatic_core_interfaces.http.request import Request
from typing_extensions import Protocol

from apimatic_core.templating.json_pointer_resolver import JsonPointerResolver


# ======================================================
# Interface for all expression resolvers
# ======================================================
class ExprResolver(Protocol):
    """
    Interface for resolving runtime expressions into byte values.

    A resolver determines if it can handle a given expression, and if so,
    provides a callable that extracts the appropriate value from a Request.

    Methods:
        matches(expr): Returns True if the expression should be handled.
        compile(expr): Returns a callable that takes a Request and returns
                       the resolved value as bytes.
    """
    def matches(self, expr: str) -> bool: ...
    def compile(self, expr: str) -> Callable[[Request], bytes]: ...


# ======================================================
# Concrete resolver implementations
# ======================================================

class MethodResolver:
    """Resolves `{$method}` to the uppercased HTTP method."""
    def matches(self, expr: str) -> bool: return expr == "method"
    def compile(self, expr: str) -> Callable[[Request], bytes]:
        return lambda r: ((r.method or "").upper()).encode("utf-8")


class UrlResolver:
    """Resolves `{$url}` to the full URL of the request."""
    def matches(self, expr: str) -> bool: return expr == "url"
    def compile(self, expr: str) -> Callable[[Request], bytes]:
        return lambda r: (r.url or "").encode("utf-8")


class PathResolver:
    """Resolves `{$request.path}` to the request path."""
    def matches(self, expr: str) -> bool: return expr == "request.path"
    def compile(self, expr: str) -> Callable[[Request], bytes]:
        return lambda r: (r.path or "").encode("utf-8")


class HeaderResolver:
    """Resolves `{$request.header.<HeaderName>}` to the value of a specific header."""
    _prefix = "request.header."
    def matches(self, expr: str) -> bool: return expr.startswith(self._prefix)
    def compile(self, expr: str) -> Callable[[Request], bytes]:
        name = expr[len(self._prefix):].lower()
        def fn(r: Request) -> bytes:
            hdrs = {str(k).lower(): str(v) for k, v in (r.headers or {}).items()}
            return (hdrs.get(name, "")).encode("utf-8")
        return fn


class QueryResolver:
    """Resolves `{$request.query.<ParamName>}` to the first value of a query parameter."""
    _prefix = "request.query."
    def matches(self, expr: str) -> bool: return expr.startswith(self._prefix)
    def compile(self, expr: str) -> Callable[[Request], bytes]:
        key = expr[len(self._prefix):]
        def norm(q: Optional[Mapping[str, Union[str, Iterable[str]]]]) -> Dict[str, List[str]]:
            out: Dict[str, List[str]] = {}
            if not isinstance(q, Mapping):
                return out
            for k, v in q.items():
                kk = str(k)
                if isinstance(v, str):
                    out[kk] = [v]
                elif isinstance(v, Iterable):
                    out[kk] = [str(x) for x in v]
                else:
                    out[kk] = [str(v)]
            return out
        return lambda r: (norm(getattr(r, "query", None)).get(key, [""])[0]).encode("utf-8")


class JsonBodyPointerResolver:
    """Resolves `{$request.body#/json/pointer}` to a value in the JSON body via RFC 6901 pointer."""
    _prefix = "request.body#/"
    def matches(self, expr: str) -> bool: return expr.startswith(self._prefix)
    def compile(self, expr: str) -> Callable[[Request], bytes]:
        ptr = expr[len("request.body#"):]  # keep leading '/'
        def fn(r: Request) -> bytes:
            jpr = JsonPointerResolver(body_text=getattr(r, "body", None))
            return jpr.resolve_as_bytes(ptr)
        return fn