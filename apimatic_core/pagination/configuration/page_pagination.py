from apimatic_core_interfaces.pagination.paginated_data_manager import PaginationDataManager

class PagePagination(PaginationDataManager):
    def __init__(self, input_key):
        self.input_key = input_key
        self.next_request_builder = None

    def is_valid(self, paginated_data):
        self.next_request_builder = paginated_data.get_last_endpoint_config().request_builder

        if self.input_key is None:
            return False

        is_updated = {'updated': False}

        def updater(old_value):
            new_value = int(old_value) + 1
            is_updated['updated'] = True
            return new_value

        self.next_request_builder.update_by_reference(self.input_key, updater)

        return is_updated['updated']

    def get_next_request_builder(self, paginated_data):
        return self.next_request_builder
