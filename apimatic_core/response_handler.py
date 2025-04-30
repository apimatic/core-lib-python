import re
from apimatic_core.http.response.api_response import ApiResponse
from apimatic_core.pagination.paginated_data import PaginatedData
from apimatic_core.types.error_case import ErrorCase


class ResponseHandler:

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
        self._pagination_deserializer = None

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

    def paginated_deserializer(self, page_class, converter, return_type_getter, *data_managers):
        """
        Setter for the deserializer to be used in page-based pagination.

        :param page_class: Class for the page structure.
        :param converter: Function to convert a page to a list of items.
        :param return_type_getter: Function to convert PaginatedData to the desired return type.
        :param data_managers: Optional pagination data managers.
        :return: ResponseHandlerBuilder instance.
        """
        self._pagination_deserializer = lambda res, gc, ec: PaginatedData(
            page_class, converter, res, ec, gc, *data_managers
        ).convert(return_type_getter)
        return self

    def handle(self, response, global_config, config):

        # checking Nullify 404
        if response.status_code == 404 and self._is_nullify404:
            return None

        # validating response if configured
        self.validate(response, global_config.get_global_errors())

        # applying deserializer if configured
        deserialized_value = self.apply_deserializer(response, global_config, config)

        # applying api_response if configured
        deserialized_value = self.apply_api_response(response, deserialized_value)

        # applying convertor if configured
        deserialized_value = self.apply_convertor(deserialized_value)

        return deserialized_value

    def validate(self, response, global_errors):
        if response.status_code in range(200, 300):
            return

        self.validate_against_error_cases(response, self._local_errors)

        self.validate_against_error_cases(response, global_errors)

    def apply_xml_deserializer(self, response):
        if self._xml_item_name:
            return self._deserializer(response.text, self._xml_item_name, self._deserialize_into)
        return self._deserializer(response.text, self._deserialize_into)

    def apply_deserializer(self, response, global_config, config):
        if self._is_xml_response:
            return self.apply_xml_deserializer(response)
        elif self._deserialize_into:
            return self._deserializer(response.text, self._deserialize_into)
        elif self._deserializer and not self._datetime_format:
            return self._deserializer(response.text)
        elif self._deserializer and self._datetime_format:
            return self._deserializer(response.text, self._datetime_format)
        elif self._pagination_deserializer:
            return self._pagination_deserializer(response, global_config, config)
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

    @staticmethod
    def validate_against_error_cases(response, error_cases):
        actual_status_code = str(response.status_code)
        # Handling error case when configured as explicit error code
        error_case = error_cases.get(actual_status_code) if error_cases else None
        if error_case:
            error_case.raise_exception(response)

        # Handling error case when configured as explicit error codes range
        default_range_error_case = [error_cases[status_code] for status_code, error_case in error_cases.items()
                                    if re.match(r'^[{}]XX$'.format(actual_status_code[0]),
                                                status_code)] if error_cases else None
        if default_range_error_case:
            default_range_error_case[0].raise_exception(response)

        # Handling default error case if configured
        default_error_case = error_cases.get('default') if error_cases else None
        if default_error_case:
            default_error_case.raise_exception(response)
