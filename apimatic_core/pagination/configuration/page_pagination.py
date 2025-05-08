from apimatic_core.pagination.configuration.pagination_data_manager import PaginationDataManager

class PagePagination(PaginationDataManager):
    def __init__(self, input_key):
        self.input_key = input_key

    def is_valid(self, paginated_data, next_request_builder):
        if self.input_key is None:
            return False

        is_updated = {'updated': False}

        def updater(old_value):
            try:
                new_value = int(old_value) + 1
                is_updated['updated'] = True
                return new_value
            except (ValueError, TypeError):
                return old_value

        next_request_builder.update_by_reference(self.input_key, updater)

        return is_updated['updated']
