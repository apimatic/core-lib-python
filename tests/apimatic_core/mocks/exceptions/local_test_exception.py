from typing import Optional

from apimatic_core_interfaces.http.http_response import HttpResponse
from pydantic import BaseModel, Field, AliasChoices
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.mocks.exceptions.api_exception import APIException
from tests.apimatic_core.mocks.exceptions.global_test_exception import GlobalTestException


class LocalTestExceptionValidator(BaseModel):
    secret_message_for_endpoint: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("secret_message_for_endpoint", "SecretMessageForEndpoint"),
              serialization_alias="SecretMessageForEndpoint")
    ] = None

class LocalTestException(GlobalTestException):
    secret_message_for_endpoint: Optional[str] = None

    def __init__(self, reason: str, response: HttpResponse):
        """Constructor for the LocalTestException class

        Args:
            reason (string): The reason (or error message) for the Exception
                to be raised.
            response (HttpResponse): The HttpResponse of the API call.

        """
        super(LocalTestException, self).__init__(reason, response)
        dictionary = ApiHelper.json_deserialize(self.response.text) or {}
        validated_data = LocalTestExceptionValidator(**dictionary)
        self.secret_message_for_endpoint = validated_data.secret_message_for_endpoint
