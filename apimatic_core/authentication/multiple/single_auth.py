from apimatic_core_interfaces.authentication.authentication import Authentication
from apimatic_core_interfaces.http.http_request import HttpRequest
from pydantic import validate_call
from typing import Dict, Optional


class Single(Authentication):

    @property
    def error_message(self) -> str:
        return "[{}]".format(self._error_message)

    @validate_call
    def __init__(self, auth_participant: str):
        super(Single, self).__init__()
        self._auth_participant = auth_participant
        self._mapped_auth: Optional[Authentication] = None
        self._error_message: Optional[str] = None
        self._is_valid: bool = False

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def with_auth_managers(self, auth_managers: Dict[str, Authentication]) -> Authentication:
        if not auth_managers.get(self._auth_participant):
            raise ValueError("Auth key is invalid.")

        self._mapped_auth = auth_managers[self._auth_participant]

        return self

    @validate_call
    def is_valid(self) -> bool:
        self._is_valid = self._mapped_auth.is_valid() if self._mapped_auth else False
        if not self._is_valid:
            self._error_message = self._mapped_auth.error_message if self._mapped_auth else "Invalid auth key."

        return self._is_valid

    @validate_call
    def apply(self, http_request: HttpRequest):

        if self._mapped_auth is None or not self._is_valid:
            return

        self._mapped_auth.apply(http_request)

