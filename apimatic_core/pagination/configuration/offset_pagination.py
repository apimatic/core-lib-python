from apimatic_core_interfaces.pagination.paginated_data_manager import PaginationDataManager

class OffsetPagination(PaginationDataManager):
    """Pagination manager implementation for offset-based pagination."""

    def __init__(self, input_):
        """
        Initializes a new instance of the OffsetPagination class.

        Args:
            input_ (str): JSON pointer to the request field representing the offset.
        """
        self.input = input_
        self._next_req_builder = None

    def is_valid(self, paginated_data):
        """Checks if the input is valid and updates the offset in the request."""
        self._next_req_builder = paginated_data.get_last_request_builder()

        if self.input is None:
            return False

        is_updated = {"value": False}

        def update_func(old):
            try:
                new_value = int(str(old)) + paginated_data.get_last_data_size()
                is_updated["value"] = True
                return new_value
            except (ValueError, TypeError):
                return old

        self._next_req_builder.update_by_reference(self.input, update_func)
        return is_updated["value"]

    def get_next_request_builder(self, paginated_data):
        """Returns the updated request builder with the new offset value."""
        return self._next_req_builder
