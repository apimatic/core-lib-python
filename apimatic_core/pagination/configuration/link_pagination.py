from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper


class LinkPagination(PaginationStrategy):
    """Pagination manager implementation for link-based pagination."""

    @property
    def metadata(self):
        return self._metadata_creator(self._next_link)

    def __init__(self, next_link_pointer, metadata_creator):
        super().__init__(metadata_creator)

        if next_link_pointer is None:
            raise ValueError("Next link pointer for cursor based pagination cannot be None")

        self._next_link_pointer = next_link_pointer
        self._next_link = None

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder

        if last_response is None:
            return request_builder

        self._next_link = ApiHelper.resolve_response_pointer(
            self._next_link_pointer,
            last_response.text,
            last_response.headers
        )

        if self._next_link is None:
            return None

        query_params = ApiHelper.get_query_parameters(self._next_link)
        updated_query_params = request_builder.query_params.copy()
        updated_query_params.update(query_params)

        return request_builder.clone_with(
            query_params=updated_query_params
        )
