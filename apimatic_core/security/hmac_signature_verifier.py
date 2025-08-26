import base64
import hashlib
import hmac
from enum import Enum
from typing import Mapping, Optional, Sequence, Protocol

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier
from apimatic_core_interfaces.types.event_request import EventRequest

from apimatic_core.exceptions.signature_verification_error import SignatureVerificationError


class DigestEncoder(Protocol):
    """Encodes raw HMAC digest bytes into the on-wire string."""
    def encode(self, digest: bytes) -> str: ...


class HexEncoder:
    def encode(self, digest: bytes) -> str:
        return digest.hex()


class Base64Encoder:
    def encode(self, digest: bytes) -> str:
        return base64.b64encode(digest).decode("utf-8")


class Base64UrlEncoder:
    def encode(self, digest: bytes) -> str:
        # Trim '=' padding to match many providers’ behavior
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

class HmacOrder(Enum):
    """Defines how additional headers are combined with the body in the HMAC message."""
    PREPEND = "prepend"
    APPEND = "append"

class HmacSignatureVerifier(SignatureVerifier):
    """
    HMAC-SHA256 verifier with pluggable digest encoder and flexible message shape.

    Behavior:
        - Returns True on valid signature.
        - Raises SignatureVerificationError when the signature header is missing
          or the signature does not match.
        - Raises ValueError for invalid inputs (misuse).
    """

    def __init__(
        self,
        *,
        key: str,
        signature_header: str = "X-Signature",
        additional_headers: Optional[Sequence[str]] = None,
        order: HmacOrder = HmacOrder.PREPEND,
        delimiter: str = "|",
        encoder: DigestEncoder = HexEncoder(),
        hash_alg=hashlib.sha256,
    ):
        if not isinstance(key, str) or not key:
            raise ValueError("HMAC key must be a non-empty string.")
        if not isinstance(signature_header, str) or not signature_header.strip():
            raise ValueError("signature_header must be a non-empty string.")
        if not isinstance(delimiter, str) or not delimiter:
            raise ValueError("delimiter must be a non-empty string.")
        if order not in (HmacOrder.PREPEND, HmacOrder.APPEND):
            raise ValueError("order must be HmacOrder.PREPEND or HmacOrder.APPEND.")

        self._key_bytes = key.encode("utf-8")
        self._sig_header = signature_header.lower().strip()
        self._headers = [h.lower().strip() for h in (additional_headers or ())]
        self._order = order
        self._delimiter = delimiter
        self._encoder = encoder
        self._hash_alg = hash_alg

    def verify(self, request: EventRequest) -> bool:
        if request is None or not isinstance(request, EventRequest):
            raise ValueError("request must be an EventRequest.")

        if not isinstance(request.body, str):
            raise ValueError("request.body must be a str (raw JSON).")

        # normalize headers
        normalized: Mapping[str, str] = {
            str(k).lower(): str(v) for k, v in request.headers.items()
        }
        provided = normalized.get(self._sig_header)
        if provided is None or not str(provided).strip():
            raise SignatureVerificationError(
                f"Signature header '{self._sig_header}' is missing from the request."
            )
        provided = str(provided).strip()

        # Build canonical message
        parts: list[str] = []
        if self._order is HmacOrder.PREPEND:
            for h in self._headers:
                val = normalized.get(h)
                if val is not None:
                    parts.append(str(val).strip())
            parts.append(request.body)
        else:
            parts.append(request.body)
            for h in self._headers:
                val = normalized.get(h)
                if val is not None:
                    parts.append(str(val).strip())

        message = self._delimiter.join(parts).encode("utf-8")

        try:
            digest = hmac.new(self._key_bytes, message, self._hash_alg).digest()
            expected = self._encoder.encode(digest)
            return hmac.compare_digest(provided, expected)
        except Exception as e:
            raise SignatureVerificationError("HMAC digest computation failed.") from e