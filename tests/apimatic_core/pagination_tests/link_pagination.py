from apimatic_core.types.parameter import Parameter
from tests.apimatic_core.mocks.pagination.paginated_data import PaginatedData
from apimatic_core.request_builder import RequestBuilder
from tests.apimatic_core.base import Base
from apimatic_core.pagination.configuration.link_pagination import LinkPagination


class TestLinkPagination(Base):

    def test_valid_link_returns_true(self):
        request_builder = RequestBuilder()
        response_body = '{"next": "https://api.example.com?page=2"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        link = LinkPagination("$response.body#/next")

        assert link.is_valid(paginated_data)
        assert link.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "2"
            return value

        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", update_func)

    def test_valid_link_with_additional_params_returns_true(self):
        request_builder = RequestBuilder() \
            .query_param(Parameter().key("size").value(456)) \
            .query_param(Parameter().key("page").value(1)) \
            .header_param(Parameter().key("page").value(2))
        response_body = '{"next": "https://api.example.com?page=2"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        link = LinkPagination("$response.body#/next")

        assert link.is_valid(paginated_data)

        def assert_page(v):
            assert v == "2"
            return v

        def assert_size(v):
            assert v == 456
            return v

        def assert_header(v):
            assert v == 2
            return v

        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", assert_page)
        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/size", assert_size)
        link.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/page", assert_header)

    def test_valid_link_from_header_returns_true(self):
        request_builder = RequestBuilder()
        response_headers = {"next": "https://api.example.com?page=2"}
        paginated_data = PaginatedData(request_builder=request_builder, response_headers=response_headers)

        link = LinkPagination("$response.headers#/next")

        assert link.is_valid(paginated_data)

        def assert_header(v):
            assert v == '2'
            return v

        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", assert_header)

    def test_invalid_pointer_returns_false(self):
        request_builder = RequestBuilder()
        response_body = '{"next": "https://api.example.com?page=2"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        link = LinkPagination("$response.body#/next/href")

        assert not link.is_valid(paginated_data)

    def test_missing_response_returns_false(self):
        request_builder = RequestBuilder()
        paginated_data = PaginatedData(request_builder=request_builder, response_body=None)

        link = LinkPagination("$response.body#/next")

        assert not link.is_valid(paginated_data)

    def test_missing_pointer_returns_false(self):
        request_builder = RequestBuilder()
        response_body = '{"next": "https://api.example.com?page=2"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        link = LinkPagination(None)

        assert not link.is_valid(paginated_data)

    def test_multiple_query_params_returns_true(self):
        request_builder = RequestBuilder()
        response_body = '{"next": "https://api.example.com?page=2&size=5"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        link = LinkPagination("$response.body#/next")

        assert link.is_valid(paginated_data)

        def assert_page(v):
            assert v == '2'
            return v

        def assert_size(v):
            assert v == '5'
            return v

        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", assert_page)
        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/size", assert_size)

    def test_encoded_query_params_returns_true(self):
        request_builder = RequestBuilder()
        response_body = '{"next": "https://api.example.com?page%20o=2%20a&size%20q=5^%214$"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        link = LinkPagination("$response.body#/next")

        assert link.is_valid(paginated_data)

        def assert_page(v):
            assert v == "2 a"
            return v

        def assert_size(v):
            assert v == "5^!4$"
            return v

        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page o", assert_page)
        link.get_next_request_builder(paginated_data).update_by_reference("$request.query#/size q", assert_size)
