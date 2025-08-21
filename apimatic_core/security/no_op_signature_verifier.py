from typing import Mapping

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier


class NoOpSignatureVerifier(SignatureVerifier):
    """
    Verifier that always returns True.
    Useful for testing or when verification is disabled.
    """

    def verify(self, headers: Mapping[str, str], payload: str) -> bool:
        """
        Always returns True regardless of input.

        Args:
            headers (Mapping[str, str]): HTTP headers (ignored).
            payload (str): Raw request body (ignored).

        Returns:
            bool: Always True.
        """
        return True