from apimatic_core.pagination.paginated_data import PaginatedData
from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper


class OffsetPagination(PaginationStrategy):
    """Pagination manager implementation for offset-based pagination."""

    def __init__(self, input_):
        """
        Initializes a new instance of the OffsetPagination class.

        Args:
            input_ (str): JSON pointer to the request field representing the offset.
        """
        if input_ is None:
            raise ValueError("Input pointer for offset based pagination cannot be None")

        self._input = input_
        self._offset = 0

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder
        last_page_size = paginated_data.page_size
        # The last response is none which means this is going to be the 1st page
        if last_response is None:
            self._offset = self._get_initial_offset(request_builder)
            return request_builder

        self._offset += last_page_size

        return self.get_updated_request_builder(request_builder, self._input, self._offset)

    def _get_initial_offset(self, request_builder):
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)

        if path_prefix == "$request.path":
            return int(ApiHelper.get_value_by_json_pointer(request_builder.template_params, field_path))
        elif path_prefix == "$request.query":
            return int(ApiHelper.get_value_by_json_pointer(request_builder.query_params, field_path))
        elif path_prefix == "$request.headers":
            return int(ApiHelper.get_value_by_json_pointer(request_builder.header_params, field_path))

        return 0