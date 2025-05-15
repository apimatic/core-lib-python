from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper


class LinkPagination(PaginationStrategy):
    """Pagination manager implementation for link-based pagination."""

    def __init__(self, next_link):
        """
        Initializes a new instance of the LinkPagination class.

        Args:
            next (str): JSON pointer of a field in the response, representing the next request query URL.
        """
        if next_link is None:
            raise ValueError("Next link pointer for cursor based pagination cannot be None")
        self._next_link = next_link

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder

        if last_response is None:
            return request_builder

        link_value = ApiHelper.resolve_response_pointer(
            self._next_link,
            last_response.text,
            last_response.headers
        )

        if link_value is None:
            return None

        query_params = ApiHelper.get_query_parameters(link_value)
        updated_query_params = request_builder.query_params.copy()
        updated_query_params.update(query_params)

        return request_builder.clone_with(
            query_params=updated_query_params
        )

