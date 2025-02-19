"""
This is an exception class which will be raised when union type validation fails.
"""
from pydantic import validate_call


class OneOfValidationException(Exception):

    @validate_call
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
