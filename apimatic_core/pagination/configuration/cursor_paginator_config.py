class CursorPaginatedConfiguration:
    def __init__(self, next_cursor=None, cursor_query_param_name=None, result_pointer=None):
        self.next_cursor = next_cursor
        self.cursor_query_param_name = cursor_query_param_name
        self.result_pointer = result_pointer

    def set_next_cursor(self, next_cursor):
        self.next_cursor = next_cursor
        return self

    def set_cursor_query_param_name(self, cursor_query_param_name):
        self.cursor_query_param_name = cursor_query_param_name
        return self

    def set_result_pointer(self, result_pointer):
        self.result_pointer = result_pointer
        return self
