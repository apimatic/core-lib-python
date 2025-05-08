from apimatic_core.pagination.configuration.pagination_data_manager import PaginationDataManager

class OffsetPagination(PaginationDataManager):
    """Pagination manager implementation for offset-based pagination."""

    def __init__(self, input_):
        """
        Initializes a new instance of the OffsetPagination class.

        Args:
            input_ (str): JSON pointer to the request field representing the offset.
        """
        self.input = input_

    def is_valid(self, paginated_data, next_req_builder):
        """Checks if the input is valid and updates the offset in the request."""

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

        next_req_builder.update_by_reference(self.input, update_func)
        return is_updated["value"]

