from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper

class PagePagination(PaginationStrategy):
    """
    Implements a page-based pagination strategy for API requests.

    This class manages pagination by updating the request builder with the appropriate page number,
    using a JSON pointer to identify the pagination parameter. It also applies a metadata wrapper
    to each paged response, including the current page number.
    """

    def __init__(self, input_, metadata_wrapper):
        """
        Initializes a PagePagination instance with the given input pointer and metadata wrapper.

        Args:
            input_: The JSON pointer indicating the pagination parameter in the request.
            metadata_wrapper: A callable for wrapping pagination metadata.

        Raises:
            ValueError: If input_ is None.
        """
        super().__init__(metadata_wrapper)

        if input_ is None:
            raise ValueError("Input pointer for page based pagination cannot be None")

        self._input = input_
        self._page_number = 1

    def apply(self, paginated_data):
        """
        Updates the request builder to fetch the next page of results based on the current paginated data.

        Args:
            paginated_data: An object containing the last response, request builder, and page size.

        Returns:
            The updated request builder configured for the next page request.
        """
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder
        last_page_size = paginated_data.page_size
        # The last response is none which means this is going to be the 1st page
        if last_response is None:
            self._page_number = self._get_initial_page_offset(request_builder)
            return request_builder
        self._page_number += 1 if last_page_size > 0 else 0

        return self.get_updated_request_builder(request_builder, self._input, self._page_number)

    def apply_metadata_wrapper(self, paged_response):
        """
        Applies the metadata wrapper to the paged response, including the current page number.

        Args:
            paged_response: The response object for the current page.

        Returns:
            The result of the metadata wrapper with the paged response and current page number.
        """
        return self._metadata_wrapper(paged_response, self._page_number)

    def _get_initial_page_offset(self, request_builder):
        """
        Determines the initial page offset for pagination by extracting the value from the request builder
        based on the configured JSON pointer. Returns 1 if the value is missing or invalid.

        Args:
            request_builder: The request builder containing path, query, and header parameters.

        Returns:
            int: The initial page offset value.
        """
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)

        try:
            if path_prefix == "$request.path":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.template_params, field_path))
            elif path_prefix == "$request.query":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.query_params, field_path))
            elif path_prefix == "$request.headers":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.header_params, field_path))
        except ValueError:
            pass
        return 1
