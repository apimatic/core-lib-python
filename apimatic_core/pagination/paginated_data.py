from apimatic_core.http.http_call_context import HttpCallContext
from collections.abc import Iterator
import copy

class PaginatedData(Iterator):

    @property
    def last_response(self):
        return self._http_call_context.response

    @property
    def request_builder(self):
        if self.last_response is None:
            return self._initial_request_builder

        return self._api_call.request_builder

    @property
    def page_size(self):
        return len(self._page)

    def __init__(self, api_call):
        self._api_call = copy.deepcopy(api_call)
        self._initial_request_builder = api_call.request_builder
        self._pagination_strategies = self._api_call.get_pagination_stategies
        self._http_call_context =\
            self._api_call.global_configuration.get_http_client_configuration().http_callback or HttpCallContext()
        _http_client_configuration = self._api_call.global_configuration.get_http_client_configuration().clone(
            http_callback=self._http_call_context)
        self._global_configuration = self._api_call.global_configuration.clone_with(
            http_client_configuration=_http_client_configuration)
        self._page = []
        self._current_index = 0

    def __iter__(self):
        return self._get_new_self_instance()

    def __next__(self):
        if self._current_index >= self.page_size:
            self._page = self._fetch_next_converted_page()
            self._current_index = 0

        if not self._page:
            raise StopIteration

        item = self._page[self._current_index]
        self._current_index += 1
        return item

    def pages(self):
        """
        Generator to iterate over pages instead of items.
        """
        # Create a new instance so the page iteration is independent
        paginated_data = self._get_new_self_instance()

        while True:
            paginated_data._page = paginated_data._fetch_next_page()
            if not paginated_data._page:
                break
            yield paginated_data._page

    def _fetch_next_page(self):
        for pagination_strategy in self._pagination_strategies:
            request_builder = pagination_strategy.apply(self)
            if request_builder is None:
                continue
            try:
                return self._api_call.clone(
                    global_configuration=self._global_configuration, request_builder=request_builder
                ).execute()
            except Exception as ex:
                raise ex
        return []


    def _fetch_next_converted_page(self):
        for pagination_strategy in self._pagination_strategies:
            request_builder = pagination_strategy.apply(self)
            if request_builder is None:
                continue
            try:
                response = self._api_call.clone(
                    global_configuration=self._global_configuration, request_builder=request_builder
                ).execute()
                return self._api_call.get_paginated_item_converter(response)
            except Exception as ex:
                raise ex
        return []

    def _get_new_self_instance(self):
        return PaginatedData(self._api_call.clone(request_builder=self._initial_request_builder))
