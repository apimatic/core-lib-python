import pytest

from apimatic_core.pagination.paginated_data import PaginatedData
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.request_builder import RequestBuilder
from apimatic_core.pagination.strategies.offset_pagination import OffsetPagination

class TestOffsetPagination:

    @pytest.fixture
    def mock_metadata_wrapper(self, mocker):
        return mocker.Mock(name="metadata_wrapper_mock")

    @pytest.fixture
    def mock_request_builder(self, mocker):
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
                new_rb._template_params = self.template_params.copy()
                new_rb._query_params = self.query_params.copy()
                new_rb._header_params = self.header_params.copy()

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
        paginated_data.last_response = None
        paginated_data.request_builder = mock_request_builder
        paginated_data.page_size = 0
        return paginated_data

    @pytest.fixture
    def mock_paginated_data_subsequent_call(self, mocker, mock_request_builder, mock_last_response):
        paginated_data = mocker.Mock(spec=PaginatedData)
        paginated_data.last_response = mock_last_response
        paginated_data.request_builder = mock_request_builder
        paginated_data.page_size = 10
        return paginated_data

    def _create_offset_pagination_instance(self, input_value, metadata_wrapper):
        """Helper to create an OffsetPagination instance."""
        return OffsetPagination(input_=input_value, metadata_wrapper=metadata_wrapper)

    # --- Test __init__ ---
    def test_init_success(self, mock_metadata_wrapper):
        op = self._create_offset_pagination_instance("$request.query#/offset", mock_metadata_wrapper)
        assert op._input == "$request.query#/offset"
        assert op._metadata_wrapper == mock_metadata_wrapper
        assert op._offset == 0

    def test_init_input_none_raises_error(self, mock_metadata_wrapper):
        with pytest.raises(ValueError, match="Input pointer for offset based pagination cannot be None"):
            self._create_offset_pagination_instance(None, mock_metadata_wrapper)

    def test_init_metadata_wrapper_none_raises_error(self):
        with pytest.raises(ValueError, match="Metadata wrapper for the pagination cannot be None"):
            self._create_offset_pagination_instance("$request.query#/offset", None)

    # --- Test apply ---
    def test_apply_initial_call_with_offset_from_query(self, mocker, mock_paginated_data_initial_call,
                                                       mock_request_builder):
        mock_get_initial_request_param_value = mocker.patch.object(OffsetPagination, '_get_initial_request_param_value', return_value=100)

        op = self._create_offset_pagination_instance("$request.query#/offset", mocker.Mock())
        result_rb = op.apply(mock_paginated_data_initial_call)

        mock_get_initial_request_param_value.assert_called_once_with(mock_request_builder, "$request.query#/offset")
        assert op._offset == 100
        assert result_rb == mock_request_builder

    def test_apply_subsequent_call_increments_offset_and_updates_builder(self, mocker,
                                                                         mock_paginated_data_subsequent_call,
                                                                         mock_request_builder):
        op = self._create_offset_pagination_instance("$request.query#/offset", mocker.Mock())
        op._offset = 10

        mock_get_updated_request_builder = mocker.patch.object(
            OffsetPagination, 'get_updated_request_builder',
            return_value=mock_request_builder.clone_with(query_params={"offset": 20, "limit": 10})
        )

        result_rb = op.apply(mock_paginated_data_subsequent_call)

        assert op._offset == 20
        mock_get_updated_request_builder.assert_called_once_with(
            mock_request_builder, "$request.query#/offset", 20
        )
        assert result_rb.query_params["offset"] == 20

    # --- Test apply_metadata_wrapper ---
    def test_apply_metadata_wrapper(self, mock_metadata_wrapper, mocker):
        mock_metadata_wrapper.return_value = "wrapped_response_with_offset"

        op = self._create_offset_pagination_instance("$request.query#/offset", mock_metadata_wrapper)
        op._offset = 50
        mock_page_response = mocker.Mock()

        result = op.apply_metadata_wrapper(mock_page_response)

        mock_metadata_wrapper.assert_called_once_with(mock_page_response, 50)
        assert result == "wrapped_response_with_offset"

    # --- Test _get_initial_request_param_value ---
    @pytest.mark.parametrize(
        "input_pointer, initial_params, expected_value, json_pointer_return_value",
        [
            ("$request.path#/offset", {"offset": 50}, 50, "50"),
            ("$request.query#/offset", {"offset": 100, "limit": 20}, 100, "100"),
            ("$request.headers#/offset", {"offset": 200}, 200, "200"),
            ("$request.query#/offset", {"limit": 20}, 0, None),  # No value found
            ("invalid_prefix#/offset", {"offset": 10}, 0, "10"),  # Invalid prefix, should default to 0
        ]
    )
    def test_get_initial_offset_various_scenarios(self, mocker, mock_request_builder, mock_metadata_wrapper,
                                                   input_pointer, initial_params, expected_value, json_pointer_return_value):
        # Dynamically set params based on the test case
        if "$request.path" in input_pointer:
            mock_request_builder._template_params = initial_params
        elif "$request.query" in input_pointer:
            mock_request_builder._query_params = initial_params
        elif "$request.headers" in input_pointer:
            mock_request_builder._header_params = initial_params

        # Mocks
        mock_split_into_parts = mocker.patch.object(ApiHelper, 'split_into_parts',
                                                    return_value=(input_pointer.split('#')[0], input_pointer.split('#')[1]))
        mock_get_value_by_json_pointer = mocker.patch.object(ApiHelper, 'get_value_by_json_pointer',
                                                             return_value=json_pointer_return_value)

        op = self._create_offset_pagination_instance(input_pointer, mock_metadata_wrapper)
        result = op._get_initial_request_param_value(mock_request_builder, input_pointer)

        mock_split_into_parts.assert_called_once_with(input_pointer)

        # Assertions for mock calls based on prefix validity
        if input_pointer.startswith(("$request.path", "$request.query", "$request.headers")):
            # Determine which params dict was accessed
            accessed_params = None
            if "$request.path" in input_pointer:
                accessed_params = mock_request_builder.template_params
            elif "$request.query" in input_pointer:
                accessed_params = mock_request_builder.query_params
            elif "$request.headers" in input_pointer:
                accessed_params = mock_request_builder.header_params

            mock_get_value_by_json_pointer.assert_called_once_with(accessed_params, input_pointer.split('#')[1])
        else:
            mock_get_value_by_json_pointer.assert_not_called()

        assert result == expected_value