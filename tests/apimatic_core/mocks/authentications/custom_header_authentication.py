
from __future__ import annotations
from typing import Dict, Optional
from apimatic_core.authentication.header_auth import HeaderAuth
from pydantic import BaseModel, validate_call

class CustomHeaderAuthenticationCredentials(BaseModel):

    token: str

    def clone_with(self, token: Optional[str]=None) -> 'CustomHeaderAuthenticationCredentials':
        return CustomHeaderAuthenticationCredentials(token=token or self.token)

class CustomHeaderAuthentication(HeaderAuth):
    @property
    def error_message(self) -> str:
        """Display error message on occurrence of authentication failure
        in OAuthBearerToken

        """
        return "CustomHeaderAuthentication: token is undefined."

    @validate_call
    def __init__(
            self, custom_header_authentication_credentials: Optional['CustomHeaderAuthenticationCredentials']):
        auth_params: Dict[str, str] = {}
        if custom_header_authentication_credentials is not None \
                and custom_header_authentication_credentials.token is not None:
            auth_params = {"token": custom_header_authentication_credentials.token}
        super().__init__(auth_params=auth_params)
