
from __future__ import annotations
from typing import Dict, Optional

from apimatic_core.authentication.header_auth import HeaderAuth
from apimatic_core.utilities.auth_helper import AuthHelper
from pydantic import BaseModel, validate_call


class BasicAuthCredentials(BaseModel):
    username: str
    password: str

    def clone_with(self,
                   username: Optional[str]=None,
                   password: Optional[str]=None) -> 'BasicAuthCredentials':
        return BasicAuthCredentials(
            username=username or self.username,
            password=password or self.password)

class BasicAuth(HeaderAuth):

    @property
    def error_message(self) -> str:
        """Display error message on occurrence of authentication failure
        in BasicAuth

        """
        return "BasicAuth: username or password is undefined."

    @validate_call
    def __init__(self, basic_auth_credentials: Optional['BasicAuthCredentials']) -> None:
        auth_params: Dict[str, str] = {}
        if basic_auth_credentials is not None \
                and basic_auth_credentials.username and basic_auth_credentials.password:
            auth_params = {"Basic-Authorization": "Basic {}".format(
                AuthHelper.get_base64_encoded_value(basic_auth_credentials.username, basic_auth_credentials.password))}
        super().__init__(auth_params=auth_params)
