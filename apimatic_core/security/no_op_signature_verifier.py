from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier
from apimatic_core_interfaces.http.request import Request


class NoOpSignatureVerifier(SignatureVerifier):
    """
    Verifier that always returns True.
    Useful for testing or when verification is disabled.
    """

    def verify(self, request: Request) -> bool:
        """
        Always returns True regardless of input.

        Args:
            request: Framework-agnostic HTTP request snapshot used by verifiers and the webhook manager.

        Returns:
            bool: Always True.
        """
        return True