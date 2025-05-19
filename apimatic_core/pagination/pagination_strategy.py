# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from apimatic_core.utilities.api_helper import ApiHelper


class PaginationStrategy(ABC):
    """
    Abstract base class for implementing pagination strategies.

    Provides methods to initialize with pagination metadata, apply pagination logic to request builders,
    and update request builders with new pagination parameters based on JSON pointers.
    """

    def __init__(self, metadata_wrapper):
        """
        Initializes the PaginationStrategy with the provided metadata wrapper.

        Args:
            metadata_wrapper: An object containing pagination metadata. Must not be None.

        Raises:
            ValueError: If metadata_wrapper is None.
        """
        if metadata_wrapper is None:
            raise ValueError("Metadata wrapper for the pagination cannot be None")

        self._metadata_wrapper = metadata_wrapper

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

    @abstractmethod
    def apply_metadata_wrapper(self, paged_response):
        """
        Processes the paged API response using the metadata wrapper.

        Args:
            paged_response: The response object containing paginated data.

        Returns:
            The processed response with applied pagination metadata.
        """
        ...

    @staticmethod
    def get_updated_request_builder(request_builder, input_pointer, offset):
        """
        Updates the given request builder by modifying its path, query,
         or header parameters based on the specified JSON pointer and offset.

        Args:
            request_builder: The request builder instance to update.
            input_pointer (str): JSON pointer indicating which parameter to update.
            offset: The value to set at the specified parameter location.

        Returns:
            The updated request builder with the modified parameter.
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