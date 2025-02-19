from typing import Optional

from apimatic_core_interfaces.http.http_response import HttpResponse
from pydantic import BaseModel, Field, AliasChoices
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.mocks.exceptions.api_exception import APIException


class GlobalTestExceptionValidator(BaseModel):
    server_message: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("server_message", "ServerMessage"),
              serialization_alias="ServerMessage")
    ] = None
    server_code: Annotated[
        Optional[int],
        Field(validation_alias=AliasChoices("server_code", "ServerCode"),
              serialization_alias="ServerCode")
    ] = None

class GlobalTestException(APIException):
    server_message: Optional[str] = None
    server_code: Optional[int] = None

    def __init__(self, reason: str, response: HttpResponse):
        """Constructor for the GlobalTestException class

        Args:
            reason (string): The reason (or error message) for the Exception
                to be raised.
            response (HttpResponse): The HttpResponse of the API call.

        """
        super(GlobalTestException, self).__init__(reason, response)
        dictionary = ApiHelper.json_deserialize(self.response.text) or {}
        validated_data = GlobalTestExceptionValidator(**dictionary)
        self.server_message = validated_data.server_message
        self.server_code = validated_data.server_code
