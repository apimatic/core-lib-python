from apimatic_core_interfaces.pagination.paginated_data_manager import PaginationDataManager
from apimatic_core.types.parameter import Parameter


class OffsetPagination(PaginationDataManager):
    """Pagination manager implementation for offset-based pagination.

    This class increments an offset query parameter by the size of the last page's data
    to build the request for the next page.
    """

    def __init__(self, input_):
        """
        Initializes a new instance of the OffsetPagination class.

        Args:
            input_ (str): The name of the query parameter that holds the offset value.
        """
        self.input = input_
        self.next_req_builder = None

    def is_valid(self, paginated_data):
        """Checks if a next page can be requested based on the offset value.

        Args:
            paginated_data: The paginated response data.

        Returns:
            bool: True if the offset parameter exists and a next page request can be built, False otherwise.
        """
        if self.input is None:
            return False

        try:
            last_request = paginated_data.get_last_endpoint_config().get_request_builder()
            req_query = last_request.build(
                paginated_data.get_last_global_config
            ).query_parameters

            if self.input in req_query:
                next_offset_value = int(str(req_query[self.input])) + paginated_data.get_last_data_size()
                self.next_req_builder = last_request.query_param(
                    Parameter()
                    .key(self.input)
                    .value(next_offset_value)
                )
                return True

        except Exception:
            pass

        return False

    def get_next_request_builder(self, paginated_data):
        """Returns the next request builder with the updated offset value.

        Args:
            paginated_data: The paginated response data.

        Returns:
            HttpRequest.Builder: A builder instance for the next page request.
        """
        return self.next_req_builder
