from apimatic_core.pagination.pagination_strategy import PaginationStrategy
from apimatic_core.utilities.api_helper import ApiHelper

class PagePagination(PaginationStrategy):

    @property
    def metadata(self):
        return self._metadata_creator(self._page_number)

    def __init__(self, input_, metadata_creator):
        super().__init__(metadata_creator)

        if input_ is None:
            raise ValueError("Input pointer for page based pagination cannot be None")

        self._input = input_
        self._page_number = 1

    def apply(self, paginated_data):
        last_response = paginated_data.last_response
        request_builder = paginated_data.request_builder
        last_page_size = paginated_data.page_size
        # The last response is none which means this is going to be the 1st page
        if last_response is None:
            self._page_number = self._get_initial_page_offset(request_builder)
            return request_builder
        self._page_number += 1 if last_page_size > 0 else 0

        return self.get_updated_request_builder(request_builder, self._input, self._page_number)

    def _get_initial_page_offset(self, request_builder):
        path_prefix, field_path = ApiHelper.split_into_parts(self._input)

        try:
            if path_prefix == "$request.path":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.template_params, field_path))
            elif path_prefix == "$request.query":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.query_params, field_path))
            elif path_prefix == "$request.headers":
                return int(ApiHelper.get_value_by_json_pointer(request_builder.header_params, field_path))
        except Exception:
            pass
        return 1
