from __future__ import annotations
import re

from typing import Callable, Union, Any, Optional, Dict, List, Type, Literal

from apimatic_core_interfaces.formats.datetime_format import DateTimeFormat
from apimatic_core_interfaces.http.http_response import HttpResponse
from pydantic import validate_call

from apimatic_core.http.response.api_response import ApiResponse
from apimatic_core.types.error_case import ErrorCase, MessageType


class ResponseHandler:

    def __init__(self):
        self._deserializer: Any = None
        self._convertor: Optional[Callable[[Any], Any]] = None
        self._deserialize_into: Any = None
        self._is_api_response: bool = False
        self._is_nullify404: bool = False
        self._local_errors: Dict[str, ErrorCase] = {}
        self._datetime_format: Optional[DateTimeFormat] = None
        self._is_xml_response: bool = False
        self._xml_item_name: Optional[str] = None

    @validate_call
    def deserializer(self, deserializer: Any) -> 'ResponseHandler':
        self._deserializer = deserializer
        return self

    @validate_call
    def convertor(self, convertor: Optional[Callable[[Any], Any]]) -> 'ResponseHandler':
        self._convertor = convertor
        return self

    @validate_call
    def deserialize_into(self, deserialize_into: Any) -> 'ResponseHandler':
        self._deserialize_into = deserialize_into
        return self

    @validate_call
    def is_api_response(self, is_api_response: bool) -> 'ResponseHandler':
        self._is_api_response = is_api_response
        return self

    @validate_call
    def is_nullify404(self, is_nullify404: bool) -> 'ResponseHandler':
        self._is_nullify404 = is_nullify404
        return self

    @validate_call
    def local_error(
            self, error_code: Union[int, str], error_message: str, exception_type: Type[Any]
    ) -> 'ResponseHandler':
        self._local_errors[str(error_code)] = ErrorCase(message=error_message,
                                                        message_type=MessageType.SIMPLE,
                                                        exception_type=exception_type)
        return self

    @validate_call
    def local_error_template(
            self, error_code: Union[int, str], error_message: str, exception_type: Type[Any]
    ) -> 'ResponseHandler':
        self._local_errors[str(error_code)] = ErrorCase(message=error_message,
                                                        message_type=MessageType.TEMPLATE,
                                                        exception_type=exception_type)
        return self

    @validate_call
    def datetime_format(self, datetime_format: DateTimeFormat) -> 'ResponseHandler':
        self._datetime_format = datetime_format
        return self

    @validate_call
    def is_xml_response(self, is_xml_response: bool) -> 'ResponseHandler':
        self._is_xml_response = is_xml_response
        return self

    @validate_call
    def xml_item_name(self, xml_item_name: Optional[str]) -> 'ResponseHandler':
        self._xml_item_name = xml_item_name
        return self

    @validate_call
    def handle(self, response: HttpResponse, global_errors: Dict[str, ErrorCase]) -> Any:

        # checking Nullify 404
        if response.status_code == 404 and self._is_nullify404:
            return None

        # validating response if configured
        self.validate(response, global_errors)

        # applying deserializer if configured
        deserialized_value = self.apply_deserializer(response)

        # applying api_response if configured
        deserialized_value = self.apply_api_response(response, deserialized_value)

        # applying convertor if configured
        deserialized_value = self.apply_convertor(deserialized_value)

        return deserialized_value

    @validate_call
    def validate(self, response: HttpResponse, global_errors: Dict[str, ErrorCase]):
        if response.status_code in range(200, 300):
            return

        self.validate_against_error_cases(response, self._local_errors)

        self.validate_against_error_cases(response, global_errors)

    @validate_call
    def apply_xml_deserializer(self, response: HttpResponse) -> Any:
        if self._deserializer is None:
            return

        if self._xml_item_name:
            return self._deserializer(response.text, self._xml_item_name, self._deserialize_into)
        return self._deserializer(response.text, self._deserialize_into)

    @validate_call
    def apply_deserializer(self, response: HttpResponse) -> Any:
        if self._is_xml_response:
            return self.apply_xml_deserializer(response)
        elif self._deserialize_into:
            return self._deserializer(response.text, self._deserialize_into)
        elif self._deserializer and not self._datetime_format:
            return self._deserializer(response.text)
        elif self._deserializer and self._datetime_format:
            return self._deserializer(response.text, self._datetime_format)
        else:
            return response.text

    @validate_call
    def apply_api_response(self, response: HttpResponse, deserialized_value: Any) -> Any:
        if self._is_api_response:
            return ApiResponse(response, body=deserialized_value,
                               errors=deserialized_value.get('errors') if type(deserialized_value) is dict else None)

        return deserialized_value

    @validate_call
    def apply_convertor(self, deserialized_value: Any) -> Any:
        if self._convertor:
            return self._convertor(deserialized_value)

        return deserialized_value

    @staticmethod
    @validate_call
    def validate_against_error_cases(response: HttpResponse, error_cases: Dict[str, ErrorCase]):
        actual_status_code: str = str(response.status_code)
        # Handling error case when configured as explicit error code
        error_case: Optional[ErrorCase] = error_cases.get(actual_status_code) if error_cases else None
        if error_case:
            error_case.raise_exception(response)

        # Handling error case when configured as explicit error codes range
        default_range_error_case: Optional[List[ErrorCase]] = [
            error_cases[status_code]
            for status_code, error_case in error_cases.items()
            if re.match(r'^[{}]XX$'.format(actual_status_code[0]), status_code)
        ] if error_cases else None
        if default_range_error_case:
            default_range_error_case[0].raise_exception(response)

        # Handling default error case if configured
        default_error_case: Optional[ErrorCase] = error_cases.get('default') if error_cases else None
        if default_error_case:
            default_error_case.raise_exception(response)
