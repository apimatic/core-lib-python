"""
This is an exception class which will be raised when verifying the Webhooks & Callbacks signature.
"""


class SignatureVerificationError(Exception):
    """Raised when a request cannot be verified (missing or invalid signature)."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
