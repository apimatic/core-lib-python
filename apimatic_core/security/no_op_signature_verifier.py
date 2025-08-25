from typing import Mapping

from apimatic_core_interfaces.security.signature_verifier import SignatureVerifier
from apimatic_core_interfaces.types.event_request import EventRequest


class NoOpSignatureVerifier(SignatureVerifier):
    """
    Verifier that always returns True.
    Useful for testing or when verification is disabled.
    """

    def verify(self, request: EventRequest) -> bool:
        """
        Always returns True regardless of input.

        Args:
            request: The incoming event request.

        Returns:
            bool: Always True.
        """
        return True