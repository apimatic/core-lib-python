from abc import abstractmethod

from apimatic_core_interfaces.authentication.authentication import Authentication
from apimatic_core_interfaces.http.http_request import HttpRequest
from pydantic import validate_call
from typing import Dict

from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.auth_helper import AuthHelper


class QueryAuth(Authentication):

    @property
    @abstractmethod
    def error_message(self) -> str:
        ...

    def with_auth_managers(self, auth_managers: Dict[str, 'Authentication']):
        pass

    @validate_call
    def __init__(self, auth_params: Dict[str, str]):
        self._auth_params = auth_params

    def is_valid(self) -> bool:
        return AuthHelper.is_valid_auth(self._auth_params)

    @validate_call
    def apply(self, http_request: HttpRequest):
        for key, value in self._auth_params.items():
            self._add_query_parameter(key, value, http_request)

    @validate_call
    def _add_query_parameter(self, key: str, value: str, http_request: HttpRequest):
        query_url = ApiHelper.append_url_with_query_parameters(
            http_request.query_url,
            {key: value}
        )
        http_request.query_url = ApiHelper.clean_url(query_url)
