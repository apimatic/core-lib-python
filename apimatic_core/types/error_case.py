import re
from enum import Enum

from apimatic_core_interfaces.http.http_response import HttpResponse
from pydantic import validate_call, BaseModel
from typing import Optional, Literal

from apimatic_core.utilities.api_helper import ApiHelper


class MessageType(str, Enum):
    SIMPLE = 'simple'
    TEMPLATE = 'template'

class ErrorCase(BaseModel):
    message: str
    message_type: MessageType = MessageType.SIMPLE
    exception_type: type

    @validate_call
    def raise_exception(self, response: HttpResponse):
        """Raises the exception for the current error case type.
            Args:
                response (HttpResponse): The received http response.
            """
        if self.message_type == MessageType.TEMPLATE:
            raise self.exception_type(self._get_resolved_error_message_template(response), response)

        raise self.exception_type(self.message, response)

    @validate_call
    def _get_resolved_error_message_template(self, response: HttpResponse):
        """Updates all placeholders in the given message template with provided value.

                Args:
                    response (HttpResponse): The received http response.

                Returns:
                    string: The resolved template value.
                """
        placeholders = re.findall(r'\{\$.*?\}', self.message)

        status_code_placeholder = set(filter(lambda element: element == '{$statusCode}', placeholders))
        header_placeholders = set(filter(lambda element: element.startswith('{$response.header'), placeholders))
        body_placeholders = set(filter(lambda element: element.startswith('{$response.body'), placeholders))

        # Handling response code placeholder
        error_message_template = ApiHelper.resolve_template_placeholders(
            status_code_placeholder, str(response.status_code), self.message)

        # Handling response header placeholder
        error_message_template = ApiHelper.resolve_template_placeholders(
            header_placeholders, response.headers, error_message_template)

        # Handling response body placeholder
        response_payload = ApiHelper.json_deserialize(str(response.text), as_dict=True)
        error_message_template = ApiHelper.resolve_template_placeholders_using_json_pointer(
            body_placeholders, response_payload, error_message_template)

        return error_message_template
