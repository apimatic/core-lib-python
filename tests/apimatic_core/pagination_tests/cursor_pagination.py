import pytest

from apimatic_core.types.parameter import Parameter
from tests.apimatic_core.mocks.pagination.paginated_data import PaginatedData
from apimatic_core.request_builder import RequestBuilder
from tests.apimatic_core.base import Base
from apimatic_core.pagination.configuration.cursor_pagination import CursorPagination


class TestCursorPagination(Base):

    def test_with_valid_cursor_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.query#/cursor")

        assert cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "xyz123"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.query#/cursor", update_func)

    def test_with_valid_cursor_and_different_type1_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.query#/cursor")

        assert cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "123"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.query#/cursor", update_func)

    def test_with_valid_cursor_and_different_type2_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("cursor").value(456))
        response_body = '{"next_cursor": 123}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.query#/cursor")

        assert cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == 123
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.query#/cursor", update_func)

    def test_with_valid_cursor_but_missing_in_first_request_returns_false(self):
        request_builder = RequestBuilder()
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.query#/cursor")

        assert not cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            pytest.fail("Should not be called")

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.query#/cursor", update_func)

    def test_with_valid_cursor_from_response_header_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("cursor").value("abc"))
        response_headers = {"next_cursor": "xyz123"}
        paginated_data = PaginatedData(request_builder=request_builder, response_headers=response_headers)

        cursor = CursorPagination("$response.headers#/next_cursor", "$request.query#/cursor")

        assert cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "xyz123"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.query#/cursor", update_func)

    def test_with_valid_cursor_in_template_param_returns_true(self):
        request_builder = RequestBuilder().template_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.path#/cursor")

        assert cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "xyz123"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.path#/cursor", update_func)

    def test_with_valid_cursor_in_header_param_returns_true(self):
        request_builder = RequestBuilder().header_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.headers#/cursor")

        assert cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "xyz123"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/cursor", update_func)

    def test_with_invalid_response_pointer_returns_false(self):
        request_builder = RequestBuilder().header_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next", "$request.headers#/cursor")

        assert not cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "abc"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/cursor", update_func)

    def test_with_missing_response_pointer_returns_false(self):
        request_builder = RequestBuilder().header_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination('', "$request.headers#/cursor")

        assert not cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "abc"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/cursor", update_func)

    def test_with_invalid_request_pointer_returns_false(self):
        request_builder = RequestBuilder().header_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", "$request.headers#/next_cursor")

        assert not cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "abc"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/cursor", update_func)

    def test_with_missing_request_pointer_returns_false(self):
        request_builder = RequestBuilder().header_param(Parameter().key("cursor").value("abc"))
        response_body = '{"next_cursor": "xyz123"}'
        paginated_data = PaginatedData(request_builder=request_builder, response_body=response_body)

        cursor = CursorPagination("$response.body#/next_cursor", '')

        assert not cursor.is_valid(paginated_data)
        assert cursor.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            assert value == "abc"
            return value

        cursor.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/cursor", update_func)
