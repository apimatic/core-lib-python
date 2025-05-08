from apimatic_core.pagination.configuration.pagination_data_manager import PaginationDataManager
from apimatic_core.utilities.api_helper import ApiHelper


class CursorPagination(PaginationDataManager):
    def __init__(self, output=None, input_=None):
        self.output = output
        self.input = input_

    def is_valid(self, paginated_data, next_req_builder):

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
            next_req_builder.update_by_reference(self.input, update_func)

        return is_updated["value"]
