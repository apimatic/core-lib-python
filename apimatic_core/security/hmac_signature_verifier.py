import hashlib
import hmac
from typing import Mapping

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier
from apimatic_core_interfaces.types.event_request import EventRequest


class HmacSignatureVerifier(SignatureVerifier):
    """
    Verifier that checks webhook signatures using HMAC-SHA256.
    """

    def __init__(self, key: str, signature_header: str):
        """
        Initialize the HMAC signature verifier.

        Args:
            key (str): Secret key used for HMAC verification.
            signature_header (str): Name of the HTTP header that carries the signature.

        Raises:
            ValueError: If key or signature_header is empty.
        """
        if not key:
            raise ValueError("HMAC verification requires a non-empty key.")
        if not signature_header:
            raise ValueError("signature_header must be a non-empty string.")

        self._key = key
        self._signature_header = signature_header.lower()

    def verify(self, request: EventRequest) -> bool:
        """Check the HMAC signature against the request body.

        Args:
            request: The incoming event request.

        Returns:
            True if the signature in `X-Signature` matches the computed HMAC
            of the raw body; otherwise False.

        Raises:
            TypeError: If input types are invalid.
            ValueError: If the signature header is missing.
        """
        headers = request.headers
        payload = request.body
        if headers is None or not hasattr(headers, "items"):
            raise TypeError("headers must be a Mapping[str, str]")
        if payload is None or not isinstance(payload, str):
            raise TypeError("payload must be a str containing raw JSON")

        normalized = {k.lower(): v for k, v in headers.items()}
        provided = normalized.get(self._signature_header)
        if not provided:
            raise ValueError(f"Missing required header: {self._signature_header}")

        computed = hmac.new(
            self._key.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(provided, computed)