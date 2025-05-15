from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper

class PagePagination(PaginationStrategy):
    def __init__(self, input_):
        """
        Initializes a new instance of the OffsetPagination class.

        Args:
            input_ (str): JSON pointer to the request field representing the offset.
        """
        if input_ is None:
            raise ValueError("Input pointer for page based pagination cannot be None")

        self._input = input_
        self._page_number = 1

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder
        last_page_size = paginated_data.page_size
        # The last response is none which means this is going to be the 1st page
        if last_response is None:
            self._page_number = self._get_initial_page_offset(request_builder)
            return request_builder
        self._page_number += 1 if last_page_size > 0 else 0

        return self._get_updated_request_builder(request_builder, last_page_size)

    def _get_updated_request_builder(self, request_builder, last_page_size):
        """
        Updates the given request builder with the new offset or cursor value for pagination.

        Depending on the JSON pointer prefix, updates the appropriate field in the path, query, or headers
        with the new offset or cursor value, and returns a cloned request builder with these updated parameters.

        Args:
            request_builder: The request builder instance to update.

        Returns:
            A new request builder instance with updated pagination parameters.
        """
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)
        template_params = request_builder.template_params
        query_params = request_builder.query_params
        header_params = request_builder.header_params
        self._page_number += 1 if last_page_size > 0 else 0

        if path_prefix == "$request.path":
            template_params = ApiHelper.update_entry_by_json_pointer(
                template_params.copy(), field_path, self._page_number, inplace=True)
        elif path_prefix == "$request.query":
            query_params = ApiHelper.update_entry_by_json_pointer(
                query_params.copy(), field_path, self._page_number, inplace=True)
        elif path_prefix == "$request.headers":
            header_params = ApiHelper.update_entry_by_json_pointer(
                header_params.copy(), field_path, self._page_number, inplace=True)

        return request_builder.clone_with(
            template_params=template_params,
            query_params=query_params,
            header_params=header_params
        )

    def _get_initial_page_offset(self, request_builder):
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)

        try:
            if path_prefix == "$request.path":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.template_params, field_path))
            elif path_prefix == "$request.query":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.query_params, field_path))
            elif path_prefix == "$request.headers":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.header_params, field_path))
        except Exception:
            pass
        return 1
