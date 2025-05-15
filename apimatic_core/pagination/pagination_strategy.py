# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from apimatic_core.utilities.api_helper import ApiHelper


class PaginationStrategy(ABC):
    """An interface for managing pagination in API responses.

    This class should not be instantiated directly but should be subclassed
    to provide specific pagination management logic for paginated API responses.
    """

    @abstractmethod
    def apply(self, paginated_data):
        """
        Modifies the request builder to fetch the next page of results based on the provided paginated data.

        Args:
            paginated_data: The response data from the previous API call.

        Returns:
            RequestBuilder: An updated request builder configured for the next page request.
        """
        ...

    @staticmethod
    def get_updated_request_builder(request_builder, input_pointer, offset):
        """
        Updates the provided request builder with a new pagination offset or cursor value.

        Depending on the JSON pointer prefix, modifies the appropriate field in the path, query, or headers,
        and returns a cloned request builder with the updated pagination parameter.

        Args:
            request_builder: The request builder instance to update.
            input_pointer (str): JSON pointer indicating which parameter to update.
            offset: The new offset or cursor value for pagination.

        Returns:
            A new request builder instance with the updated pagination parameter.
        """
        path_prefix, field_path = ApiHelper.split_into_parts(input_pointer)
        template_params = request_builder.template_params
        query_params = request_builder.query_params
        header_params = request_builder.header_params

        if path_prefix == "$request.path":
            template_params = ApiHelper.update_entry_by_json_pointer(
                template_params.copy(), field_path, offset, inplace=True)
        elif path_prefix == "$request.query":
            query_params = ApiHelper.update_entry_by_json_pointer(
                query_params.copy(), field_path, offset, inplace=True)
        elif path_prefix == "$request.headers":
            header_params = ApiHelper.update_entry_by_json_pointer(
                header_params.copy(), field_path, offset, inplace=True)

        return request_builder.clone_with(
            template_params=template_params,
            query_params=query_params,
            header_params=header_params
        )