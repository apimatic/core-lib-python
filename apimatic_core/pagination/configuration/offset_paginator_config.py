from jsonpointer import resolve_pointer

from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper


class OffsetPaginatorConfiguration:
    """Configuration for OffsetPaginated."""

    def __init__(self, page_param_name=None, offset_param_name=None, result_pointer=None):
        self.page_param_name = page_param_name
        self.offset_param_name = offset_param_name
        self.result_pointer = result_pointer

    def get_next_page_req(self, request_builder, global_config, response):
        """Determines the next set of query parameters."""
        if not self.page_param_name and not self.offset_param_name:
            return request_builder  # No pagination

        req = request_builder.build(global_config)

        if self.page_param_name:
            new_page_value = int(req.query_parameters.get(self.page_param_name, 0)) + 1
            return request_builder.query_param(Parameter()
                         .key(self.page_param_name)
                         .value(new_page_value))

        if self.offset_param_name:
            extracted_value = resolve_pointer(response, self.result_pointer)
            result = ApiHelper.json_deserialize(extracted_value)

            current_offset = int(req.query_parameters.get(self.offset_param_name, 0))
            next_offset_value = current_offset + (len(result) if result else 0)

            return request_builder.query_param(Parameter()
                                               .key(self.offset_param_name)
                                               .value(next_offset_value))

        return None