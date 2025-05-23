import pytest

from apimatic_core.pagination.paginated_data import PaginatedData
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.request_builder import RequestBuilder
from apimatic_core.pagination.strategies.offset_pagination import OffsetPagination

class TestOffsetPagination:

    @pytest.fixture
    def mock_metadata_wrapper(self, mocker):
        # Reusing the mock_metadata_wrapper from previous context
        return mocker.Mock(name="metadata_wrapper_mock")

    @pytest.fixture
    def mock_request_builder(self, mocker):
        # Reusing the mock_request_builder from previous context
        class MockRequestBuilder(RequestBuilder):
            @property
            def template_params(self):
                return self._template_params

            @property
            def query_params(self):
                return self._query_params

            @property
            def header_params(self):
                return self._header_params

            def __init__(self, template_params=None, query_params=None, header_params=None):
                super().__init__()
                self._template_params = template_params if template_params is not None else {}
                self._query_params = query_params if query_params is not None else {}
                self._header_params = header_params if header_params is not None else {}

            def clone_with(self, **kwargs):
                new_rb = MockRequestBuilder()
                # Copy existing attributes
                new_rb._template_params = self.template_params.copy()
                new_rb._query_params = self.query_params.copy()
                new_rb._header_params = self.header_params.copy()

                # Apply updates from kwargs
                if 'template_params' in kwargs:
                    new_rb.template_params.update(kwargs['template_params'])
                if 'query_params' in kwargs:
                    new_rb.query_params.update(kwargs['query_params'])
                if 'header_params' in kwargs:
                    new_rb.header_params.update(kwargs['header_params'])
                return new_rb

        rb = MockRequestBuilder(
            template_params={"offset": 5},
            query_params={"offset": 10, "limit": 20},
            header_params={"offset": 15}
        )
        return rb

    @pytest.fixture
    def mock_last_response(self, mocker):
        response = mocker.Mock()
        response.text = '{"data": [{"id": 1}], "total_count": 100}'
        response.headers = {'Content-Type': 'application/json'}
        return response

    @pytest.fixture
    def mock_paginated_data_initial_call(self, mocker, mock_request_builder):
        paginated_data = mocker.Mock(spec=PaginatedData)
        paginated_data.last_response = None  # Indicates initial call
        paginated_data.request_builder = mock_request_builder
        paginated_data.page_size = 0  # Not relevant for initial call
        return paginated_data

    @pytest.fixture
    def mock_paginated_data_subsequent_call(self, mocker, mock_request_builder, mock_last_response):
        paginated_data = mocker.Mock(spec=PaginatedData)
        paginated_data.last_response = mock_last_response
        paginated_data.request_builder = mock_request_builder
        paginated_data.page_size = 10  # Assume previous page had 10 items
        return paginated_data

    # Test __init__
    def test_init_success(self, mock_metadata_wrapper):
        op = OffsetPagination(input_="$request.query#/offset", metadata_wrapper=mock_metadata_wrapper)
        assert op._input == "$request.query#/offset"
        assert op._metadata_wrapper == mock_metadata_wrapper
        assert op._offset == 0

    def test_init_input_none_raises_error(self, mock_metadata_wrapper):
        with pytest.raises(ValueError, match="Input pointer for offset based pagination cannot be None"):
            OffsetPagination(input_=None, metadata_wrapper=mock_metadata_wrapper)

    def test_init_metadata_wrapper_none_raises_error(self, mock_metadata_wrapper):
        with pytest.raises(ValueError, match="Metadata wrapper for the pagination cannot be None"):
            OffsetPagination(input_=None, metadata_wrapper=None)

    # Test apply
    def test_apply_initial_call_with_offset_from_query(self, mocker, mock_paginated_data_initial_call,
                                                       mock_request_builder):
        # Mock _get_initial_offset to return a specific value
        mock_get_initial_request_param_value = mocker.patch.object(OffsetPagination, '_get_initial_request_param_value', return_value=100)

        op = OffsetPagination(input_="$request.query#/offset", metadata_wrapper=mocker.Mock())
        result_rb = op.apply(mock_paginated_data_initial_call)

        # Assert that _get_initial_offset was called
        mock_get_initial_request_param_value.assert_called_once_with(mock_request_builder, "$request.query#/offset")
        assert op._offset == 100
        assert result_rb == mock_request_builder  # Should return the original request_builder

    def test_apply_subsequent_call_increments_offset_and_updates_builder(self, mocker,
                                                                         mock_paginated_data_subsequent_call,
                                                                         mock_request_builder):
        # Initialize the offset to simulate it being set by a previous call (e.g., test_apply_initial_call)
        # or just set it to 0 and let apply handle the first increment
        op = OffsetPagination(input_="$request.query#/offset", metadata_wrapper=mocker.Mock())
        op._offset = 10  # Simulate offset after 1st page

        # Patch get_updated_request_builder to simulate its behavior
        mock_get_updated_request_builder = mocker.patch.object(
            OffsetPagination, 'get_updated_request_builder',
            return_value=mock_request_builder.clone_with(query_params={"offset": 20, "limit": 10})
        )

        result_rb = op.apply(mock_paginated_data_subsequent_call)

        # Expected offset: initial (10) + last_page_size (10) = 20
        assert op._offset == 20
        mock_get_updated_request_builder.assert_called_once_with(
            mock_request_builder, "$request.query#/offset", 20
        )
        # Verify that the returned request builder has the updated offset
        assert result_rb.query_params["offset"] == 20

    # Test apply_metadata_wrapper
    def test_apply_metadata_wrapper(self, mock_metadata_wrapper, mocker):
        mock_metadata_wrapper.return_value = "wrapped_response_with_offset"

        op = OffsetPagination(
            input_="$request.query#/offset",
            metadata_wrapper=mock_metadata_wrapper
        )
        op._offset = 50  # Set an offset value for the test
        mock_page_response = mocker.Mock()

        result = op.apply_metadata_wrapper(mock_page_response)

        mock_metadata_wrapper.assert_called_once_with(mock_page_response, 50)
        assert result == "wrapped_response_with_offset"

    # Test _get_initial_offset
    def test_get_initial_offset_from_path(self, mocker, mock_request_builder):
        # Ensure the mock_request_builder has the value in template_params for this test
        mock_request_builder._template_params = {"offset": 50}

        mock_split_into_parts = mocker.patch.object(ApiHelper, 'split_into_parts',
                                                    return_value=("$request.path", "/offset"))
        mock_get_value_by_json_pointer = mocker.patch.object(ApiHelper, 'get_value_by_json_pointer', return_value="50")

        op = OffsetPagination(input_="$request.path#/offset", metadata_wrapper=mocker.Mock())
        result = op._get_initial_request_param_value(mock_request_builder, "$request.path#/offset")

        mock_split_into_parts.assert_called_once_with("$request.path#/offset")
        mock_get_value_by_json_pointer.assert_called_once_with(mock_request_builder.template_params, "/offset")
        assert result == 50

    def test_get_initial_offset_from_query(self, mocker, mock_request_builder, mock_metadata_wrapper):
        # Ensure the mock_request_builder has the value in query_params for this test
        mock_request_builder._query_params = {"offset": 100, "limit": 20}

        mock_split_into_parts = mocker.patch.object(ApiHelper, 'split_into_parts',
                                                    return_value=("$request.query", "/offset"))
        mock_get_value_by_json_pointer = mocker.patch.object(ApiHelper, 'get_value_by_json_pointer', return_value="100")

        op = OffsetPagination(input_="$request.query#/offset", metadata_wrapper=mock_metadata_wrapper)
        result = op._get_initial_request_param_value(mock_request_builder, "$request.query#/offset")

        mock_split_into_parts.assert_called_once_with("$request.query#/offset")
        mock_get_value_by_json_pointer.assert_called_once_with(mock_request_builder.query_params, "/offset")
        assert result == 100

    def test_get_initial_offset_from_headers(self, mocker, mock_request_builder, mock_metadata_wrapper):
        # Ensure the mock_request_builder has the value in header_params for this test
        mock_request_builder._header_params = {"offset": 200}

        mock_split_into_parts = mocker.patch.object(ApiHelper, 'split_into_parts',
                                                    return_value=("$request.headers", "/offset"))
        mock_get_value_by_json_pointer = mocker.patch.object(ApiHelper, 'get_value_by_json_pointer', return_value="200")

        op = OffsetPagination(input_="$request.headers#/offset", metadata_wrapper=mock_metadata_wrapper)
        result = op._get_initial_request_param_value(mock_request_builder, "$request.headers#/offset")

        mock_split_into_parts.assert_called_once_with("$request.headers#/offset")
        mock_get_value_by_json_pointer.assert_called_once_with(mock_request_builder.header_params, "/offset")
        assert result == 200

    def test_get_initial_offset_no_value_found(self, mocker, mock_request_builder, mock_metadata_wrapper):
        # Ensure the mock_request_builder has no 'offset' in the relevant params
        mock_request_builder._query_params = {"limit": 20}

        mock_split_into_parts = mocker.patch.object(ApiHelper, 'split_into_parts',
                                                    return_value=("$request.query", "/offset"))
        mock_get_value_by_json_pointer = mocker.patch.object(ApiHelper, 'get_value_by_json_pointer',
                                                             return_value=None)  # Simulate not found

        op = OffsetPagination(input_="$request.query#/offset", metadata_wrapper=mock_metadata_wrapper)
        result = op._get_initial_request_param_value(mock_request_builder, "$request.query#/offset")
        mock_split_into_parts.assert_called_once_with("$request.query#/offset")
        mock_get_value_by_json_pointer.assert_called_once_with(mock_request_builder.query_params, "/offset")
        assert result == 0  # Should default to 0 if not found

    def test_get_initial_offset_invalid_prefix(self, mocker, mock_request_builder, mock_metadata_wrapper):
        mock_split_into_parts = mocker.patch.object(ApiHelper, 'split_into_parts',
                                                    return_value=("invalid_prefix", "/offset"))
        # Ensure get_value_by_json_pointer is not called for invalid prefixes
        mock_get_value_by_json_pointer = mocker.patch.object(ApiHelper, 'get_value_by_json_pointer')

        op = OffsetPagination(input_="invalid_prefix#/offset", metadata_wrapper=mock_metadata_wrapper)
        result = op._get_initial_request_param_value(mock_request_builder, "invalid_prefix#/offset")

        mock_split_into_parts.assert_called_once_with("invalid_prefix#/offset")
        mock_get_value_by_json_pointer.assert_not_called()
        assert result == 0
