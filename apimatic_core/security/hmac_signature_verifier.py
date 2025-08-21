import hashlib
import hmac
from typing import Mapping

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier


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

    def verify(self, headers: Mapping[str, str], payload: str) -> bool:
        """
        Verify the payload against the signature in headers.

        Args:
            headers (Mapping[str, str]): HTTP headers of the request.
            payload (str): Raw request body as a JSON string.

        Returns:
            bool: True if the computed HMAC matches the provided signature.

        Raises:
            ValueError: If the signature header is missing.
        """
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