
from __future__ import annotations
from typing import Dict, Optional

from apimatic_core.authentication.header_auth import HeaderAuth
from pydantic import BaseModel, validate_call


class BearerAuthCredentials(BaseModel):
    access_token: str

    def clone_with(self, access_token: Optional[str]=None) -> 'BearerAuthCredentials':
        return BearerAuthCredentials(access_token=access_token or self.access_token)

class BearerAuth(HeaderAuth):

    @property
    def error_message(self) -> str:
        """Display error message on occurrence of authentication failure
        in OAuthBearerToken

        """
        return "BearerAuth: access_token is undefined."

    @validate_call
    def __init__(self, o_auth_bearer_token_credentials: Optional['BearerAuthCredentials']) -> None:
        self._access_token: Optional[str] = o_auth_bearer_token_credentials.access_token \
            if o_auth_bearer_token_credentials is not None else None
        auth_params: Dict[str, str] = {}
        if self._access_token:
            auth_params = {"Bearer-Authorization": "Bearer {}".format(self._access_token)}
        super().__init__(auth_params=auth_params)
