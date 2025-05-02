from apimatic_core_interfaces.pagination.paginated_data_manager import PaginationDataManager
from apimatic_core.utilities.api_helper import ApiHelper


class CursorPagination(PaginationDataManager):
    def __init__(self, output=None, input_=None):
        self.output = output
        self.input = input_
        self.next_req_builder = None

    def is_valid(self, paginated_data):
        self.next_req_builder = paginated_data.get_last_request_builder()

        cursor_value = ApiHelper.resolve_response_pointer(
            self.output,
            paginated_data.get_last_response(),
            paginated_data.get_last_response_headers()
        )

        if cursor_value is None:
            return False

        is_updated = {"value": False}

        def update_func(_):
            is_updated["value"] = True
            return cursor_value

        if self.input:
            self.next_req_builder.update_by_reference(self.input, update_func)

        return is_updated["value"]

    def get_next_request_builder(self, _paginated_data):
        return self.next_req_builder
