import re
from apimatic_core.http.response.api_response import ApiResponse
from apimatic_core.types.error_case import ErrorCase
from apimatic_core.utilities.api_helper import ApiHelper


class ResponseHandler:

    @staticmethod
    def resolve_error_message_template(error_message_template, response):
        """Updates all placeholders in the given message template with provided value.

                Args:
                    error_message_template: The error message template string containing placeholders.
                    response: The received http response.

                Returns:
                    string: The resolved template value.
                """
        placeholders = re.findall(r'\{\$.*?\}', error_message_template)

        status_code_placeholder = set(filter(lambda element: element == '{$statusCode}', placeholders))
        header_placeholders = set(filter(lambda element: element.startswith('{$response.header'), placeholders))
        body_placeholders = set(filter(lambda element: element.startswith('{$response.body#'), placeholders))

        # Handling response code placeholder
        error_message_template = ApiHelper.resolve_template_placeholders(status_code_placeholder,
                                                                         str(response.status_code),
                                                                         error_message_template)

        # Handling response header placeholder
        error_message_template = ApiHelper.resolve_template_placeholders(header_placeholders, response.headers,
                                                                         error_message_template)

        # Handling response body placeholder
        response_payload = ApiHelper.json_deserialize(response.text, as_dict=True)
        error_message_template = ApiHelper.resolve_template_placeholders_using_json_pointer(body_placeholders,
                                                                                            response_payload,
                                                                                            error_message_template)

        return error_message_template

    def __init__(self):
        self._deserializer = None
        self._convertor = None
        self._deserialize_into = None
        self._is_api_response = False
        self._is_nullify404 = False
        self._local_errors = {}
        self._datetime_format = None
        self._is_xml_response = False
        self._xml_item_name = None
        self._endpoint_name_for_logging = None
        self._endpoint_logger = None

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

    def local_error(self, error_code, error_message, exception_type):
        self._local_errors[str(error_code)] = ErrorCase()\
            .error_message(error_message)\
            .exception_type(exception_type)
        return self

    def local_error_template(self, error_code, error_message_template, exception_type):
        self._local_errors[str(error_code)] = ErrorCase()\
            .error_message_template(error_message_template)\
            .exception_type(exception_type)
        return self

    def datetime_format(self, datetime_format):
        self._datetime_format = datetime_format
        return self

    def is_xml_response(self, is_xml_response):
        self._is_xml_response = is_xml_response
        return self

    def xml_item_name(self, xml_item_name):
        self._xml_item_name = xml_item_name
        return self

    def endpoint_name_for_logging(self, endpoint_name_for_logging):
        self._endpoint_name_for_logging = endpoint_name_for_logging
        return self

    def endpoint_logger(self, endpoint_logger):
        self._endpoint_logger = endpoint_logger
        return self

    def handle(self, response, global_errors):
        self._endpoint_logger.info('Validating response for {}.'.format(self._endpoint_name_for_logging))

        # checking Nullify 404
        if response.status_code == 404 and self._is_nullify404:
            self._endpoint_logger.info('Status code 404 received for {}. Returning None.'.format(
                self._endpoint_name_for_logging))
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

    def validate(self, response, global_errors):
        if response.status_code in range(200, 209):
            return

        self.validate_against_error_cases(response, self._local_errors)

        self.validate_against_error_cases(response, global_errors)

    def apply_xml_deserializer(self, response):
        if self._xml_item_name:
            return self._deserializer(response.text, self._xml_item_name, self._deserialize_into)
        return self._deserializer(response.text, self._deserialize_into)

    def apply_deserializer(self, response):
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

    def apply_api_response(self, response, deserialized_value):
        if self._is_api_response:
            return ApiResponse(response, body=deserialized_value,
                               errors=deserialized_value.get('errors') if type(deserialized_value) is dict else None)

        return deserialized_value

    def apply_convertor(self, deserialized_value):
        if self._convertor:
            return self._convertor(deserialized_value)

        return deserialized_value

    def get_error_message(self, error_case, response):
        if error_case.is_error_message_template():
            return self.resolve_error_message_template(error_case.get_error_message_template(), response)
        return error_case.get_error_message()

    def validate_against_error_cases(self, response, error_cases):
        actual_status_code = str(response.status_code)
        # Handling global level error case if configured
        global_error_case = error_cases.get(actual_status_code) if error_cases else None
        if global_error_case:
            raise global_error_case.get_exception_type()(self.get_error_message(global_error_case, response), response)

        # Handling global level error case for default range if configured
        default_range_global_error_case = [error_cases[status_code] for status_code, error_case in error_cases.items()
                                           if re.match(r'^[{}]XX$'.format(actual_status_code[0]),
                                                       status_code)] if error_cases else None
        if default_range_global_error_case:
            raise default_range_global_error_case[0] \
                .get_exception_type()(self.get_error_message(default_range_global_error_case[0], response), response)

        # Handling default global level error case if configured
        global_error_default_case = error_cases.get('default') if error_cases else None
        if global_error_default_case:
            raise global_error_default_case.get_exception_type()(self.get_error_message(global_error_default_case,
                                                                                        response), response)
