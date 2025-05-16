from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper


class CursorPagination(PaginationStrategy):

    def __init__(self, output, input_, metadata_wrapper):
        super().__init__(metadata_wrapper)

        if input_ is None:
            raise ValueError("Input pointer for cursor based pagination cannot be None")
        if output is None:
            raise ValueError("Output pointer for cursor based pagination cannot be None")

        self._output = output
        self._input = input_
        self._cursor_value = None

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder

        if last_response is None:
            self._cursor_value = self._get_initial_cursor_value(request_builder, self._input)
            return request_builder

        self._cursor_value = ApiHelper.resolve_response_pointer(
            self._output,
            last_response.text,
            last_response.headers
        )

        if self._cursor_value is None:
            return None

        return self.get_updated_request_builder(request_builder, self._input, self._cursor_value)

    def apply_metadata_wrapper(self, paged_response):
        return self._metadata_wrapper(self._cursor_value, paged_response)

    @staticmethod
    def _get_initial_cursor_value(request_builder, input_pointer):
        path_prefix, field_path = ApiHelper.split_into_parts(input_pointer)

        if path_prefix == "$request.path":
            return ApiHelper.get_value_by_json_pointer(request_builder.template_params, field_path)
        elif path_prefix == "$request.query":
            return ApiHelper.get_value_by_json_pointer(request_builder.query_params, field_path)
        elif path_prefix == "$request.headers":
            return ApiHelper.get_value_by_json_pointer(request_builder.header_params, field_path)

        return None
