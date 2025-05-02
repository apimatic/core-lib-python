import pytest
from apimatic_core.pagination.configuration.page_pagination import PagePagination
from tests.apimatic_core.mocks.pagination.paginated_data import PaginatedData
from apimatic_core.request_builder import RequestBuilder
from apimatic_core.types.parameter import Parameter
from tests.apimatic_core.base import Base

class TestPagePagination(Base):

    def test_valid_page_header_returns_true(self):
        request_builder = RequestBuilder().header_param(Parameter().key("page").value("3"))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.headers#/page")

        assert page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.headers#/page", lambda v: assert_and_return(v, 4))

    def test_valid_page_template_returns_true(self):
        request_builder = RequestBuilder().template_param(Parameter().key("page").value("3"))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.path#/page")

        assert page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.path#/page", lambda v: assert_and_return(v, 4))

    def test_valid_page_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("page").value("3"))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.query#/page")

        assert page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", lambda v: assert_and_return(v, 4))

    def test_valid_page_as_inner_field_returns_true(self):
        inner_map = {"val": "1"}
        request_builder = RequestBuilder().query_param(Parameter().key("page").value(inner_map))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.query#/page/val")

        assert page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page/val", lambda v: assert_and_return(v, 2))

    def test_valid_string_page_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("page").value("5"))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.query#/page")

        assert page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", lambda v: assert_and_return(v, 6))

    def test_invalid_string_page_returns_false(self):
        request_builder = RequestBuilder().query_param(Parameter().key("page").value("5a"))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.query#/page")

        assert not page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", lambda v: assert_and_return(v, "5a"))

    def test_missing_page_returns_false(self):
        request_builder = RequestBuilder()
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination("$request.query#/page")

        assert not page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            pytest.fail("Should not be called")
            return value

        page.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", update_func)

    def test_null_pointer_returns_false(self):
        request_builder = RequestBuilder().query_param(Parameter().key("page").value("5"))
        paginated_data = PaginatedData(request_builder=request_builder)

        page = PagePagination(None)

        assert not page.is_valid(paginated_data)
        assert page.get_next_request_builder(paginated_data) is not None

        page.get_next_request_builder(paginated_data).update_by_reference("$request.query#/page", lambda v: assert_and_return(v, '5'))


def assert_and_return(actual, expected):
    assert actual == expected
    return actual
