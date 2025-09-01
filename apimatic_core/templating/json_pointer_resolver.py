import json
from typing import Any, Optional
from jsonpointer import resolve_pointer, JsonPointerException


class JsonPointerResolver:
    """
    Resolve RFC 6901 JSON Pointer values from a request body string.

    Features:
      - Lazy JSON parsing (parses only once on init)
      - Canonical encoding for dict/list
      - Consistent bytes conversion for scalar values

    Usage:
        resolver = JsonPointerResolver(body_text='{"event":{"id":"123"}}')
        value_bytes = resolver.resolve_as_bytes("/event/id")
        print(value_bytes)  # b'123'
    """

    __slots__ = ("_json",)

    def __init__(self, *, body_text: Optional[str]) -> None:
        """
        Initialize a new JSON Pointer resolver.

        Args:
            body_text: JSON text body (string). None or invalid JSON results in a no-op resolver.
        """
        self._json = self._parse_json_maybe(body_text)

    def resolve(self, pointer: str) -> Any:
        """
        Resolve the value at the provided pointer.

        Args:
            pointer: JSON pointer path (e.g., "/event/id").

        Returns:
            The Python value (str, int, dict, list, etc.), or None if not found.
        """
        if self._json is None:
            return None
        try:
            return resolve_pointer(self._json, pointer)
        except JsonPointerException:
            return None

    def resolve_as_bytes(self, pointer: str) -> bytes:
        """
        Resolve the value and return as a canonical byte sequence.

        Conversion rules:
            - None: b""
            - dict/list: canonical JSON with sorted keys
            - str/int/float/bool: string representation encoded in UTF-8
            - bytes/bytearray: returned as-is
        """
        val = self.resolve(pointer)
        return self._to_bytes(val)

    @staticmethod
    def _parse_json_maybe(body: Optional[str]) -> Any:
        if not isinstance(body, str) or not body.strip():
            return None
        try:
            return json.loads(body)
        except Exception:
            return None

    @staticmethod
    def _to_bytes(val: Any) -> bytes:
        if val is None:
            return b""
        if isinstance(val, (bytes, bytearray)):
            return bytes(val)
        if isinstance(val, (dict, list)):
            return json.dumps(val, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return str(val).encode("utf-8")
