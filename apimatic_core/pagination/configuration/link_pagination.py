from apimatic_core.pagination.configuration.pagination_data_manager import PaginationDataManager
from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper


class LinkPagination(PaginationDataManager):
    """Pagination manager implementation for link-based pagination."""

    def __init__(self, next_):
        """
        Initializes a new instance of the LinkPagination class.

        Args:
            next_ (str): JSON pointer of a field in the response, representing the next request query URL.
        """
        self.next = next_

    def is_valid(self, paginated_data, next_req_builder):
        """Checks if the response contains a valid link value and prepares the next request builder."""

        link_value = ApiHelper.resolve_response_pointer(
            self.next,
            paginated_data.get_last_response(),
            paginated_data.get_last_response_headers()
        )

        if link_value is None:
            return False

        query_params = ApiHelper.get_query_parameters(link_value)
        for key, value in query_params.items():
            next_req_builder.query_param(Parameter().key(key).value(value))
        return True
