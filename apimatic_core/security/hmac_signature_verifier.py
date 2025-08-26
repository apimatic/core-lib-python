import hashlib
import hmac
from typing import Mapping, Optional, Sequence

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier
from apimatic_core_interfaces.http.request import Request

from apimatic_core.exceptions.signature_verification_error import SignatureVerificationError

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
    ):
        if not isinstance(key, str) or not key:
            raise ValueError("HMAC key must be a non-empty string.")
        if not isinstance(signature_header, str) or not signature_header.strip():
            raise ValueError("signature_header must be a non-empty string.")

        self._key = key
        self._signature_header = signature_header.lower().strip()
        self._additional_headers = [h.lower().strip() for h in (additional_headers or ())]

    def verify(self, request: Request) -> bool:
        if request is None or not isinstance(request, Request):
            raise ValueError("request must be an EventRequest.")

        if not isinstance(request.body, str):
            raise ValueError("request.body must be a str (raw JSON).")

        # normalize headers
        normalized: Mapping[str, str] = {
            str(k).lower(): str(v) for k, v in request.headers.items()
        }
        provided_signature = normalized.get(self._signature_header)
        if provided_signature is None or not str(provided_signature).strip():
            raise SignatureVerificationError(
                f"Signature header '{self._signature_header}' is missing from the request."
            )

        message_parts = []
        # Append values of additional headers (if any) to message
        for h_name in self._additional_headers:
            value = normalized.get(h_name)
            if value is not None:
                message_parts.append(value)
        # Append body
        message_parts.append(request.body)

        # Build message
        message = ".".join(message_parts)

        try:
            expected_sig = hmac.new(
                self._key.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(str(provided_signature).strip(), expected_sig)
        except Exception as e:
            raise SignatureVerificationError("HMAC digest computation failed.") from e