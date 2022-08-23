from core_lib.http.response.api_response import ApiResponse
from core_lib.types.error_case import ErrorCase


class ResponseHandler:

    def __init__(
            self
    ):
        self._deserializer = None
        self._convertor = None
        self._deserialize_into = None
        self._is_api_response = False
        self._is_nullify404 = False
        self._local_errors = {}
        self._datetime_format = None

    def deserializer(self, deserializer):
        self._deserializer = deserializer
        return self

    def convertor(self, convertor):
        self._convertor = convertor
        return self

    def deserialize_into(self, deserialize_into):
        self._deserialize_into = deserialize_into
        return self

    def is_api_response(self, is_api_response):
        self._is_api_response = is_api_response
        return self

    def is_nullify404(self, is_nullify404):
        self._is_nullify404 = is_nullify404
        return self

    def local_error(self, error_code, description, exception_type):
        self._local_errors[str(error_code)] = ErrorCase().description(description).exception_type(exception_type)
        return self

    def datetime_format(self, datetime_format):
        self._datetime_format = datetime_format
        return self

    def handle(self, response, global_errors):
        # checking Nullify 404
        if response.status_code == 404 and self._is_nullify404:
            return None

        # validating response if configured
        self.validate(response, global_errors)

        # applying deserializer if configured
        deserialized_value = self.apply_deserializer(response)

        # applying convertor if configured
        deserialized_value = self.apply_convertor(response, deserialized_value)

        return deserialized_value

    def validate(self, response, global_errors):
        actual_status_code = str(response.status_code)
        if self._local_errors:
            for expected_status_code, error_case in self._local_errors.items():
                if actual_status_code == expected_status_code:
                    raise error_case.get_exception_type()(error_case.get_description(), response)

        if global_errors:
            for expected_status_code, error_case in global_errors.items():
                if actual_status_code == expected_status_code:
                    raise error_case.get_exception_type()(error_case.get_description(), response)

        if response.status_code < 200 or response.status_code > 208:
            error_case = global_errors['default']
            raise error_case.get_exception_type()(error_case.get_description(), response)

    def apply_deserializer(self, response):
        if self._deserialize_into:
            return self._deserializer(response.text, self._deserialize_into)
        elif self._deserializer and not self._datetime_format:
            return self._deserializer(response.text)
        elif self._deserializer and self._datetime_format:
            return self._deserializer(response.text, self._datetime_format)
        else:
            return response.text

    def apply_convertor(self, response, deserialized_value):
        if self._is_api_response:
            return ApiResponse(response, body=deserialized_value)
        if self._convertor:
            return self._convertor(deserialized_value)

        return deserialized_value
