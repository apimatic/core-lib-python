from apimatic_core.pagination.strategies.cursor_pagination import CursorPagination
from apimatic_core.pagination.strategies.link_pagination import LinkPagination
from apimatic_core.pagination.strategies.offset_pagination import OffsetPagination
from apimatic_core.pagination.strategies.page_pagination import PagePagination
from apimatic_core.request_builder import RequestBuilder
from apimatic_core.response_handler import ResponseHandler
from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core_interfaces.types.http_method_enum import HttpMethodEnum
from tests.apimatic_core.base import Base
from tests.apimatic_core.mocks.callables.base_uri_callable import Server
from tests.apimatic_core.mocks.models.transactions_cursored import TransactionsCursored
from tests.apimatic_core.mocks.models.transactions_linked import TransactionsLinked
from tests.apimatic_core.mocks.models.transactions_offset import TransactionsOffset
from tests.apimatic_core.mocks.pagination.paged_iterable import PagedIterable
from tests.apimatic_core.mocks.pagination.paged_api_response import CursorPagedApiResponse, OffsetPagedApiResponse, \
    LinkPagedApiResponse, NumberPagedApiResponse
from tests.apimatic_core.mocks.pagination.paged_response import NumberPagedResponse, OffsetPagedResponse, \
    CursorPagedResponse, LinkPagedResponse


class TestPaginatedApiCall(Base):

    def setup_test(self, global_config):
        self.global_config = global_config
        self.http_response_catcher = self.global_config.get_http_client_configuration().http_callback
        self.http_client = self.global_config.get_http_client_configuration().http_client
        self.api_call_builder = self.new_api_call_builder(self.global_config)

    def test_link_paginated_call_with_api_response_enabled(self):
        self.setup_test(self.paginated_global_configuration)
        size = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/links')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('page')
                         .value(1))
            .query_param(Parameter()
                         .key('size')
                         .value(size))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsLinked.from_dictionary)
            .is_api_response(True)
        ).pagination_strategies(
            LinkPagination(
                '$response.body#/links/next',
                lambda _response, _link: LinkPagedApiResponse.create(
                    _response, lambda _obj: _obj.data, _link)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

    def test_cursor_paginated_call_with_api_response_enabled(self):
        self.setup_test(self.paginated_global_configuration)
        limit = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/cursor')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('cursor')
                         .value('initial cursor'))
            .query_param(Parameter()
                         .key('limit')
                         .value(limit))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsCursored.from_dictionary)
            .is_api_response(True)
        ).pagination_strategies(
            CursorPagination(
                '$response.body#/nextCursor',
                '$request.query#/cursor',
                lambda _response, _cursor: CursorPagedApiResponse.create(
                    _response, lambda _obj: _obj.data, _cursor)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

    def test_offset_paginated_call_with_api_response_enabled(self):
        self.setup_test(self.paginated_global_configuration)
        limit = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/offset')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('offset')
                         .value(0))
            .query_param(Parameter()
                         .key('limit')
                         .value(limit))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsOffset.from_dictionary)
            .is_api_response(True)
        ).pagination_strategies(
            OffsetPagination(
                '$request.query#/offset',
                lambda _response, _offset: OffsetPagedApiResponse.create(
                    _response, lambda _obj: _obj.data, _offset)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

    def test_page_paginated_call_with_api_response_enabled(self):
        self.setup_test(self.paginated_global_configuration)
        size = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/page')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('page')
                         .value(1))
            .query_param(Parameter()
                         .key('size')
                         .value(size))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsLinked.from_dictionary)
            .is_api_response(True)
        ).pagination_strategies(
            PagePagination(
                '$request.query#/page',
                lambda _response, _page_no: NumberPagedApiResponse.create(
                    _response, lambda _obj: _obj.data, _page_no)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5



    def test_link_paginated_call_with_api_response_disabled(self):
        self.setup_test(self.paginated_global_configuration)
        size = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/links')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('page')
                         .value(1))
            .query_param(Parameter()
                         .key('size')
                         .value(size))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsLinked.from_dictionary)
        ).pagination_strategies(
            LinkPagination(
                '$response.body#/links/next',
                lambda _response, _link: LinkPagedResponse(
                    _response, lambda _obj: _obj.data, _link)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

    def test_cursor_paginated_call_with_api_response_disabled(self):
        self.setup_test(self.paginated_global_configuration)
        limit = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/cursor')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('cursor')
                         .value('initial cursor'))
            .query_param(Parameter()
                         .key('limit')
                         .value(limit))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsCursored.from_dictionary)
        ).pagination_strategies(
            CursorPagination(
                '$response.body#/nextCursor',
                '$request.query#/cursor',
                lambda _response, _cursor: CursorPagedResponse(
                    _response, lambda _obj: _obj.data, _cursor)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

    def test_offset_paginated_call_with_api_response_disabled(self):
        self.setup_test(self.paginated_global_configuration)
        limit = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/offset')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('offset')
                         .value(0))
            .query_param(Parameter()
                         .key('limit')
                         .value(limit))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsOffset.from_dictionary)
        ).pagination_strategies(
            OffsetPagination(
                '$request.query#/offset',
                lambda _response, _offset: OffsetPagedResponse(
                    _response, lambda _obj: _obj.data, _offset)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

    def test_page_paginated_call_with_api_response_disabled(self):
        self.setup_test(self.paginated_global_configuration)
        size = 5
        result = self.api_call_builder.new_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/transactions/page')
            .http_method(HttpMethodEnum.GET)
            .query_param(Parameter()
                         .key('page')
                         .value(1))
            .query_param(Parameter()
                         .key('size')
                         .value(size))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(ApiHelper.json_deserialize)
            .deserialize_into(TransactionsLinked.from_dictionary)
        ).pagination_strategies(
            PagePagination(
                '$request.query#/page',
                lambda _response, _page_no: NumberPagedResponse(
                    _response, lambda _obj: _obj.data, _page_no)
            )
        ).paginate(
            lambda _paginated_data: PagedIterable(_paginated_data),
            lambda _response: _response.data
        )

        assert isinstance(result, PagedIterable)
        paginated_data = []
        for item in result:
            paginated_data.append(item)

        assert len(paginated_data) == 20

        for page in result.pages():
            assert len(page.items()) == 5

