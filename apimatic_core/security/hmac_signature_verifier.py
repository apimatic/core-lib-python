import base64
import hashlib
import hmac
from enum import Enum
from typing import Mapping, Optional, Sequence, Protocol

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier
from apimatic_core_interfaces.http.request import Request
from apimatic_core_interfaces.security.verification_result import VerificationResult

from apimatic_core.exceptions.signature_verification_error import SignatureVerificationError


class DigestEncoder(Protocol):
    def encode(self, digest: bytes) -> str: ...


class HexEncoder:
    def encode(self, digest: bytes) -> str:
        return digest.hex()


class Base64Encoder:
    def encode(self, digest: bytes) -> str:
        return base64.b64encode(digest).decode("utf-8")


class Base64UrlEncoder:
    def encode(self, digest: bytes) -> str:
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


class HmacOrder(Enum):
    PREPEND = "prepend"
    APPEND = "append"


class HmacSignatureVerifier(SignatureVerifier):
    """
    HMAC-SHA256 verifier with pluggable digest encoder and flexible message shape.
    verify() never raises for verification outcomes; it returns VerificationResult.
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

        self._key = key
        self._sig_header = signature_header.lower().strip()
        self._headers = [h.lower().strip() for h in (additional_headers or ())]
        self._order = order
        self._delimiter = delimiter
        self._encoder = encoder
        self._hash_alg = hash_alg

    def verify(self, request: Request) -> VerificationResult:
        try:
            # Basic request shape checks
            if request is None or not hasattr(request, "headers") or not hasattr(request, "body"):
                return VerificationResult.failed(ValueError("Invalid request object."))

            normalized: Mapping[str, str] = {str(k).lower(): str(v) for k, v in request.headers.items()}
            provided = normalized.get(self._sig_header)

            if provided is None or not str(provided).strip():
                return VerificationResult.failed(ValueError(f"Signature header '{self._sig_header}' is missing."))

            # Select body
            if not isinstance(request.body, str):
                return VerificationResult.failed(ValueError("request.body must be a str (raw JSON/text)."))

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

            # Compute digest
            digest = hmac.new(self._key.encode("utf-8"), message, self._hash_alg).digest()
            expected = self._encoder.encode(digest)

            # Constant-time compare
            ok = hmac.compare_digest(str(provided).strip(), expected)
            return VerificationResult.passed() if ok else VerificationResult.failed(SignatureVerificationError("Signature mismatch."))

        except Exception as e:
            # Convert any unexpected error into a failure result
            return VerificationResult.failed(SignatureVerificationError(f"Signature Verification Failed: {e}"))
