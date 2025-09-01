# ======================================================================
# Digest encoders
# ======================================================================
import base64

from typing_extensions import Protocol

class DigestEncoder(Protocol):
    """Protocol for digest encoders. Implementations must return a text form of the raw HMAC bytes."""
    def encode(self, digest: bytes) -> str: ...


class HexEncoder:
    """Lowercase hexadecimal encoding (e.g., 'a1b2c3...')."""
    def encode(self, digest: bytes) -> str:
        return digest.hex()


class Base64Encoder:
    """Standard Base64 encoding."""
    def encode(self, digest: bytes) -> str:
        return base64.b64encode(digest).decode("utf-8")


class Base64UrlEncoder:
    """URL-safe Base64 encoding without padding (= stripped)."""
    def encode(self, digest: bytes) -> str:
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")