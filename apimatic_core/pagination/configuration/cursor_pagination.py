from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper


class CursorPagination(PaginationStrategy):
    def __init__(self, output=None, input_=None):
        if input_ is None:
            raise ValueError("Input pointer for cursor based pagination cannot be None")
        if output is None:
            raise ValueError("Output pointer for cursor based pagination cannot be None")
        self._output = output
        self._input = input_

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder

        if last_response is None:
            return request_builder

        cursor_value = ApiHelper.resolve_response_pointer(
            self._output,
            last_response.text,
            last_response.headers
        )

        if cursor_value is None:
            return None

        return self._get_updated_request_builder(request_builder, cursor_value)

    def _get_updated_request_builder(self, request_builder, cursor_value):
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)
        template_params = request_builder.template_params
        query_params = request_builder.query_params
        header_params = request_builder.header_params

        if path_prefix == "$request.path":
            template_params = ApiHelper.update_entry_by_json_pointer(
                template_params.copy(), field_path, cursor_value, inplace=True)
        elif path_prefix == "$request.query":
            query_params = ApiHelper.update_entry_by_json_pointer(
                query_params.copy(), field_path, cursor_value, inplace=True)
        elif path_prefix == "$request.headers":
            header_params = ApiHelper.update_entry_by_json_pointer(
                header_params.copy(), field_path, cursor_value, inplace=True)

        return request_builder.clone_with(
            template_params=template_params,
            query_params=query_params,
            header_params=header_params
        )