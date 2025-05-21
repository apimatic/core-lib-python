from apimatic_core.pagination.paginated_data import PaginatedData
from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper


class OffsetPagination(PaginationStrategy):
    """
    Implements offset-based pagination strategy for API responses.

    This class manages pagination by updating an offset parameter in the request builder,
    allowing sequential retrieval of paginated data. It extracts and updates the offset
    based on a configurable JSON pointer and applies a metadata wrapper to each page response.
    """

    def __init__(self, input_, metadata_wrapper):
        """
        Initializes an OffsetPagination instance with the given input pointer and metadata wrapper.

        Args:
            input_: JSON pointer indicating the pagination parameter to update.
            metadata_wrapper: Callable for handling pagination metadata.

        Raises:
            ValueError: If input_ is None.
        """
        super().__init__(metadata_wrapper)

        if input_ is None:
            raise ValueError("Input pointer for offset based pagination cannot be None")

        self._input = input_
        self._offset = 0

    def apply(self, paginated_data):
        """
        Updates the request builder to fetch the next page of results using offset-based pagination.

        If this is the first page, initializes the offset from the request builder. Otherwise,
         increments the offset by the previous page size and updates the pagination parameter.

        Args:
            paginated_data: The PaginatedData instance containing the last response, request builder, and page size.

        Returns:
            An updated request builder configured for the next page request.
        """
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder
        last_page_size = paginated_data.page_size
        # The last response is none which means this is going to be the 1st page
        if last_response is None:
            self._offset = self._get_initial_offset(request_builder)
            return request_builder

        self._offset += last_page_size

        return self.get_updated_request_builder(request_builder, self._input, self._offset)

    def apply_metadata_wrapper(self, page_response):
        """
        Applies the metadata wrapper to the given page response, passing the current offset.

        Args:
            page_response: The response object for the current page.

        Returns:
            The result of the metadata wrapper callable with the page response and offset.
        """
        return self._metadata_wrapper(page_response, self._offset)

    def _get_initial_offset(self, request_builder):
        """
        Determines the initial offset value for pagination by extracting it from the request builder
        based on the configured JSON pointer input.

        Args:
            request_builder: The request builder containing path, query, and header parameters.

        Returns:
            int: The initial offset value extracted from the appropriate request parameter, or 0 if not found.
        """
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)

        if path_prefix == "$request.path":
            return int(ApiHelper.get_value_by_json_pointer(request_builder.template_params, field_path))
        elif path_prefix == "$request.query":
            return int(ApiHelper.get_value_by_json_pointer(request_builder.query_params, field_path))
        elif path_prefix == "$request.headers":
            return int(ApiHelper.get_value_by_json_pointer(request_builder.header_params, field_path))

        return 0
