from apimatic_core_interfaces.pagination.paginated_data_manager import PaginationDataManager
from jsonpointer import resolve_pointer

from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper


class LinkPagination(PaginationDataManager):
    """Pagination manager implementation for link-based pagination.

    This class extracts a link value (usually a URL or query string) from the response body
    and adds its query parameters to the next request.
    """

    def __init__(self, next_):
        """
        Initializes a new instance of the LinkPagination class.

        Args:
            next_ (str): The JSON path or key in the response body where the link value is found.
        """
        self.next = next_
        self.link_value = None

    def is_valid(self, paginated_data):
        """Checks if the response contains a valid link value for the next page.

        Args:
            paginated_data: The paginated response data.

        Returns:
            bool: True if a link value is present, False otherwise.
        """
        response_payload = ApiHelper.json_deserialize(paginated_data.get_last_response(), as_dict=True)
        if '#' in self.next:
            node_pointer = self.next.rsplit('#')[1].rstrip('}')
            self.link_value = resolve_pointer(response_payload, node_pointer)

        return self.link_value is not None

    def get_next_request_builder(self, paginated_data):
        """Builds the next request by adding query parameters parsed from the link value.

        Args:
            paginated_data: The current paginated response data.

        Returns:
            HttpRequest.Builder: A builder instance for the next page request.
        """
        last_request_builder = paginated_data.get_last_endpoint_config().request_builder
        query_params = ApiHelper.get_query_parameters(self.link_value)
        for key, value in query_params.items():
            last_request_builder.query_param(Parameter().key(key).value(value))
        return last_request_builder
