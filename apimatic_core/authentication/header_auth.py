from abc import abstractmethod

from apimatic_core_interfaces.authentication.authentication import Authentication
from typing import Dict, Optional

from apimatic_core_interfaces.http.http_request import HttpRequest
from pydantic import validate_call

from apimatic_core.utilities.auth_helper import AuthHelper


class HeaderAuth(Authentication):

    @property
    @abstractmethod
    def error_message(self) -> str:
        ...

    def with_auth_managers(self, auth_managers: Dict[str, 'Authentication']):
        pass

    @validate_call
    def __init__(self, auth_params: Dict[str, str]):
        self._auth_params = auth_params
        self._error_message: Optional[str] = None

    def is_valid(self) -> bool:
        return AuthHelper.is_valid_auth(self._auth_params)

    @validate_call
    def apply(self, http_request: HttpRequest) -> None:
        AuthHelper.apply(self._auth_params, http_request.add_header)

