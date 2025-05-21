import pytest

from apimatic_core.types.parameter import Parameter
from tests.apimatic_core.mocks.pagination.paginated_data import PaginatedData
from apimatic_core.request_builder import RequestBuilder
from tests.apimatic_core.base import Base
from apimatic_core.pagination.strategies.offset_pagination import OffsetPagination

class TestOffsetPagination(Base):

    def test_valid_numeric_offset_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("offset").value("3"))
        paginated_data = PaginatedData(request_builder=request_builder, last_data_size=100)

        offset = OffsetPagination("$request.query#/offset")

        assert offset.is_valid(paginated_data)
        assert offset.get_next_request_builder(paginated_data) is not None

        offset.get_next_request_builder(paginated_data).update_by_reference("$request.query#/offset", lambda v: assert_and_return(v, 103))

    def test_valid_string_offset_returns_true(self):
        request_builder = RequestBuilder().query_param(Parameter().key("offset").value("5"))
        paginated_data = PaginatedData(request_builder=request_builder, last_data_size=100)

        offset = OffsetPagination("$request.query#/offset")

        assert offset.is_valid(paginated_data)
        assert offset.get_next_request_builder(paginated_data) is not None

        offset.get_next_request_builder(paginated_data).update_by_reference("$request.query#/offset", lambda v: assert_and_return(v, 105))

    def test_invalid_string_offset_returns_false(self):
        request_builder = RequestBuilder().query_param(Parameter().key("offset").value("5a"))
        paginated_data = PaginatedData(request_builder=request_builder, last_data_size=100)

        offset = OffsetPagination("$request.query#/offset")

        assert not offset.is_valid(paginated_data)
        assert offset.get_next_request_builder(paginated_data) is not None

        offset.get_next_request_builder(paginated_data).update_by_reference("$request.query#/offset", lambda v: assert_and_return(v, "5a"))

    def test_missing_offset_returns_false(self):
        request_builder = RequestBuilder()
        paginated_data = PaginatedData(request_builder=request_builder, last_data_size=100)

        offset = OffsetPagination("$request.query#/offset")

        assert not offset.is_valid(paginated_data)
        assert offset.get_next_request_builder(paginated_data) is not None

        def update_func(value):
            pytest.fail("Should not be called")
            return value

        offset.get_next_request_builder(paginated_data).update_by_reference("$request.query#/offset", update_func)

    def test_null_pointer_returns_false(self):
        request_builder = RequestBuilder().query_param(Parameter().key("offset").value("5"))
        paginated_data = PaginatedData(request_builder=request_builder, last_data_size=100)

        offset = OffsetPagination(None)

        assert not offset.is_valid(paginated_data)
        assert offset.get_next_request_builder(paginated_data) is not None

        offset.get_next_request_builder(paginated_data).update_by_reference("$request.query#/offset", lambda v: assert_and_return(v, '5'))


def assert_and_return(actual, expected):
    assert actual == expected
    return actual
