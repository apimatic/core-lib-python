import asyncio
from typing import Dict, List, Optional, Union, Any
from http.cookies import SimpleCookie
from apimatic_core_interfaces.http.request import Request

from apimatic_core.adapters.types.django_request_like import DjangoRequestLike
from apimatic_core.adapters.types.flask_request_like import FlaskRequestLike
from apimatic_core.adapters.types.starlette_request_like import StarletteRequestLike


def _as_listdict(obj: Any) -> Dict[str, List[str]]:
    """
    Normalize a query/form-like mapping to a plain `Dict[str, List[str]]`.

    Supports:
      - Objects exposing a `getlist(key)` API (e.g., Django `QueryDict`,
        Werkzeug `MultiDict`) → copies each list.
      - Plain mappings (`Mapping[str, str]`) → wraps scalar values in single-item lists.

    Args:
        obj: A mapping or MultiDict/QueryDict-like object. Falsy values return `{}`.

    Returns:
        A new dict where each key maps to a list of strings.
    """
    if not obj:
        return {}
    getlist = getattr(obj, "getlist", None)
    if callable(getlist):
        return {k: list(getlist(k)) for k in obj.keys()}
    return {k: [obj[k]] for k in obj.keys()}


async def to_unified_request(
    req: Union[StarletteRequestLike, FlaskRequestLike, DjangoRequestLike]
) -> Request:
    """
    Convert a framework request (Starlette/FastAPI, Flask/Werkzeug, or Django) to a unified snapshot.

    This function uses structural typing (Protocols) to detect the request "shape"
    at runtime and extracts a compact, immutable snapshot that excludes file uploads.

    Extraction rules:
      • Method/path/url: copied verbatim (with Starlette `url` stringified).
      • Headers: copied into a plain `dict` (case preserved as-provided by the framework).
      • Raw body: captured as bytes (Starlette: `await req.body()`; Flask: `get_data(cache=True)`;
        Django: `req.body`).
      • Query/form: normalized to `Dict[str, List[str]]` via `_as_listdict(...)`.
        For Starlette, form parsing only occurs for `multipart/form-data` or
        `application/x-www-form-urlencoded` content types, and file parts are ignored.
      • Cookies: copied to a `dict`. Flask additionally falls back to parsing the
        `Cookie` header if `req.cookies` is empty.
      • Django headers: if `req.headers` is missing/empty (very old Django),
        a best-effort fallback uses `req.META["HTTP_*"]`.

    Args:
        req: A request object structurally compatible with one of the supported
             frameworks' request shapes.

    Returns:
        Request: The framework-agnostic snapshot.

    Raises:
        TypeError: If `req` does not match any supported Protocol.
    """
    # --- Starlette/FastAPI ---
    if isinstance(req, StarletteRequestLike):
        headers = dict(req.headers)
        raw = await req.body()
        query = _as_listdict(req.query_params)
        cookies = dict(req.cookies)
        url_str = str(req.url)
        path = req.url.path
        ct = (headers.get("content-type") or headers.get("Content-Type") or "").lower()
        form: Dict[str, List[str]] = {}
        if ct.startswith(("multipart/form-data", "application/x-www-form-urlencoded")):
            form_data = await req.form()
            for k in form_data.keys():
                for v in form_data.getlist(k):
                    # Ignore file-like values (UploadFile or similar)
                    if not (hasattr(v, "filename") and hasattr(v, "read")):
                        form.setdefault(k, []).append(str(v))
        return Request(
            method=req.method,
            path=path,
            url=url_str,
            headers=headers,
            raw_body=raw,
            query=query,
            cookies=cookies,
            form=form,
        )

    # --- Flask ---
    if isinstance(req, FlaskRequestLike):
        headers = dict(req.headers)
        url_str: Optional[str] = getattr(req, "url", None)
        path: str = req.path
        raw: bytes = req.get_data(cache=True)
        query = _as_listdict(req.args)
        cookies = dict(req.cookies)
        # Best-effort cookie header fallback if the jar is empty
        if not cookies:
            cookie_header = headers.get("Cookie") or headers.get("cookie")
            if cookie_header:
                jar = SimpleCookie()
                jar.load(cookie_header)
                cookies = {k: morsel.value for k, morsel in jar.items()}
        form = _as_listdict(req.form)
        return Request(
            method=req.method,
            path=path,
            url=url_str,
            headers=headers,
            raw_body=raw,
            query=query,
            cookies=cookies,
            form=form,
        )

    # --- Django ---
    if isinstance(req, DjangoRequestLike):
        headers = dict(getattr(req, "headers", {}) or {})
        # Fallback for very old Django: META → headers
        if not headers:
            meta = getattr(req, "META", {}) or {}
            headers = {
                k[5:].replace("_", "-"): str(v)
                for k, v in meta.items()
                if k.startswith("HTTP_")
            }
        url_str = req.build_absolute_uri()
        path = req.path
        raw = bytes(getattr(req, "body", b"") or b"")
        query = _as_listdict(getattr(req, "GET", {}))
        cookies = dict(getattr(req, "COOKIES", {}) or {})
        form = _as_listdict(getattr(req, "POST", {}))
        return Request(
            method=req.method,
            path=path,
            url=url_str,
            headers=headers,
            raw_body=raw,
            query=query,
            cookies=cookies,
            form=form,
        )

    raise TypeError(f"Unsupported request type: {type(req)!r}")


def _unwrap_local_proxy(obj: Any) -> Any:
    """
    Best-effort, dependency-free unwrapping for Flask's `LocalProxy`.

    We intentionally do not import `werkzeug.local.LocalProxy` to keep this adapter
    framework-agnostic. Instead, we use duck typing: if the object exposes
    `_get_current_object()` (the LocalProxy API), we call it to retrieve the real
    underlying request. If the object is not a LocalProxy, or unwrapping fails,
    the original object is returned.

    Args:
        obj: Potentially a `LocalProxy` or any object.

    Returns:
        The unwrapped underlying object when possible; otherwise `obj` unchanged.
    """
    getter = getattr(obj, "_get_current_object", None)
    if callable(getter):
        try:
            return getter()
        except Exception:
            # If unwrapping fails for any reason, fall back to the original object.
            # The async core will still attempt structural dispatch via Protocols.
            return obj
    return obj


def to_unified_request_sync(
    req: Union[FlaskRequestLike, DjangoRequestLike]
) -> Request:
    """
    Synchronous wrapper around `to_unified_request(...)` for WSGI-style apps.

    This bridges sync Flask/Django views to the async core by:
      • Unwrapping Flask's `LocalProxy` via duck typing (no Werkzeug import).
      • Reusing the running event loop when present; otherwise creating one.
      • Delegating to the async adapter which handles structural dispatch.

    Args:
        req: A Flask- or Django-like request object (structurally typed). Passing an
             already unified `Request` snapshot is an error.

    Returns:
        Request: The framework-agnostic snapshot.

    Raises:
        TypeError: If the provided object is not a supported request shape.
    """
    # 1) Unwrap LocalProxy-like objects (no werkzeug import; duck-typing)
    req = _unwrap_local_proxy(req)

    # 3) Bridge sync -> async: run the async core in (or with) an event loop.
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No running loop in this thread (typical in WSGI). Create one.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # 4) Delegate to the single async entrypoint that handles Starlette/Flask/Django
    #    via structural typing (Protocols).
    return loop.run_until_complete(to_unified_request(req))
