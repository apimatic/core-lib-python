
from __future__ import annotations
from typing import Dict, Optional
from pydantic import BaseModel, validate_call

from apimatic_core.authentication.query_auth import QueryAuth


class CustomQueryAuthenticationCredentials(BaseModel):

    token: str
    api_key: str

    def clone_with(
            self, token: Optional[str]=None, api_key: Optional[str]=None) -> 'CustomQueryAuthenticationCredentials':
        return CustomQueryAuthenticationCredentials(token=token or self.token, api_key=api_key or self.api_key)

class CustomQueryAuthentication(QueryAuth):
    @property
    def error_message(self) -> str:
        """Display error message on occurrence of authentication failure
        in OAuthBearerToken

        """
        return "CustomQueryAuthentication: token or api_key is undefined."

    @validate_call
    def __init__(
            self, custom_query_authentication_credentials: Optional['CustomQueryAuthenticationCredentials']):
        auth_params: Dict[str, str] = {}
        if custom_query_authentication_credentials is not None \
                and custom_query_authentication_credentials.token is not None:
            auth_params["token"] = custom_query_authentication_credentials.token
        if custom_query_authentication_credentials is not None \
                and custom_query_authentication_credentials.api_key is not None:
            auth_params["api-key"] = custom_query_authentication_credentials.api_key
        super().__init__(auth_params=auth_params)
