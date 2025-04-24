from apimatic_core_interfaces.pagination.paginated_data_manager import PaginationDataManager
from jsonpointer import resolve_pointer
from apimatic_core.types.parameter import Parameter


class CursorPagination(PaginationDataManager):
    """Pagination manager implementation for cursor-based pagination.

    This class extracts a cursor value from the response body and adds it as a query parameter
    to the next request if available.
    """

    def __init__(self, output, input_):
        """
        Initializes a new instance of the CursorPagination class.

        Args:
            output (str): The JSON path or key in the response body where the cursor value is found.
            input_ (str): The query parameter key to which the cursor value should be assigned in the next request.
        """
        self.output = output
        self.input = input_
        self.cursor_value = None

    def is_valid(self, paginated_data):
        """Checks if the response contains a valid cursor value for the next page.

        Args:
            paginated_data: The paginated response data.

        Returns:
            bool: True if a cursor value is present, False otherwise.
        """
        response_body = paginated_data.get_last_response()
        self.cursor_value = resolve_pointer(response_body, self.output)
        return self.cursor_value is not None

    def get_next_request_builder(self, paginated_data):
        """Builds the next request by adding the cursor value as a query parameter.

        Args:
            paginated_data: The current paginated response data.

        Returns:
            HttpRequest.Builder: A builder instance for the next page request.
        """
        last_request_builder = paginated_data.get_last_endpoint_config().get_request_builder()
        return last_request_builder.query_param(Parameter().key(self.input).value(self.cursor_value))
