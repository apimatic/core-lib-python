from datetime import datetime, date, timezone
from typing import Any, List, Union

import pytest
from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core_interfaces.types.union_type_context import UnionTypeContext
from pydantic import validate_call

from apimatic_core.exceptions.oneof_validation_exception import OneOfValidationException
from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.one_of import OneOf
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.union_type_helper import UnionTypeHelper
from tests.apimatic_core.base import Base
from tests.apimatic_core.mocks.models.atom import Atom
from tests.apimatic_core.mocks.models.days import Days
from tests.apimatic_core.mocks.models.deer import Deer
from tests.apimatic_core.mocks.models.lion import Lion
from tests.apimatic_core.mocks.models.months import Months
from tests.apimatic_core.mocks.models.orbit import Orbit
from tests.apimatic_core.mocks.models.rabbit import Rabbit


class TestOneOf:

    @pytest.mark.parametrize(
        'input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output', [
            # Simple Cases
            (100, [LeafType(int), LeafType(str)], UnionTypeContext(), True, 100),
            (100, [LeafType(int), LeafType(int), LeafType(str)], UnionTypeContext(), False, None),
            ('abc', [LeafType(int), LeafType(str)], UnionTypeContext(), True, 'abc'),
            (True, [LeafType(bool), LeafType(str)], UnionTypeContext(), True, True),
            (100.44, [LeafType(int), LeafType(str)], UnionTypeContext(), False, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext(is_nullable=True), True, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext(is_optional=True), True, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext(), False, None),

            # Outer Array Cases
            (['abc', 'def'], [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), True, ['abc', 'def']),
            ([100, 200], [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), True, [100, 200]),
            ([100, 'abc'], [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), True, [100, 'abc']),
            (100, [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), False, None),
            ('100', [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), False, None),
            ([['abc', 'def']], [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), False, None),

            # Inner Array Cases
            (['abc', 'def'], [LeafType(int, UnionTypeContext(is_array=True)),
                              LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(), True, ['abc', 'def']),
            ([100, 200], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(), True, [100, 200]),
            ([100, 'abc'],
             [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(), False, None),

            # Partial Array Case
            ('abc', [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(), True, 'abc'),
            ([100, 200], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(), True, [100, 200]),
            ([100, 'abc'], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(), False, None),
            (100, [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(), False, None),

            # Array of Partial Arrays Cases
            (['abc', 'def'], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(is_array=True), True, ['abc', 'def']),
            ([[100, 200]], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(is_array=True), True, [[100, 200]]),
            ([[100, 200], 'abc'], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(is_array=True), True, [[100, 200], 'abc']),
            ([[100, 'abc']], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(is_array=True), False, None),
            ([100], [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str)],
             UnionTypeContext(is_array=True), False, None),

            # Array of Arrays Cases
            ([['abc', 'def'], ['def', 'ghi']], [LeafType(int, UnionTypeContext(is_array=True)),
                                                LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [['abc', 'def'], ['def', 'ghi']]),
            ([[100, 200], [300, 400]], [LeafType(int, UnionTypeContext(is_array=True)),
                                        LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[100, 200], [300, 400]]),
            ([[100, 200], ['abc', 'def']], [LeafType(int, UnionTypeContext(is_array=True)),
                                            LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[100, 200], ['abc', 'def']]),
            ([[100, 'abc'], [200, 'def']], [LeafType(int, UnionTypeContext(is_array=True)),
                                            LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
            ([[100, 'abc'], ['def', 'ghi']], [LeafType(int, UnionTypeContext(is_array=True)),
                                              LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
            ([[100.45, 200.45], [100, 200]], [LeafType(int, UnionTypeContext(is_array=True)),
                                              LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
            ([['abc', 'def'], [100.45, 200.45]], [LeafType(int, UnionTypeContext(is_array=True)),
                                                  LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),

            # Outer Dictionary Cases
            ({'key0': 'abc', 'key1': 'def'}, [LeafType(int), LeafType(str)], UnionTypeContext(is_dict=True), True,
             {'key0': 'abc', 'key1': 'def'}),
            ({'key0': 100, 'key1': 200}, [LeafType(int), LeafType(str)], UnionTypeContext(is_dict=True), True,
             {'key0': 100, 'key1': 200}),
            ({'key0': 100, 'key2': 'abc'}, [LeafType(int), LeafType(str)], UnionTypeContext(is_dict=True), True,
             {'key0': 100, 'key2': 'abc'}),
            (100, [LeafType(int), LeafType(str)], UnionTypeContext(is_dict=True), False, None),
            ('100', [LeafType(int), LeafType(str)], UnionTypeContext(is_dict=True), False, None),
            ({'key0': {'key0': 'abc', 'key1': 'def'}}, [LeafType(int), LeafType(str)],
             UnionTypeContext(is_dict=True), False, None),

            # Inner Dictionary Cases
            ({'key0': 'abc', 'key1': 'def'}, [LeafType(int, UnionTypeContext(is_dict=True)),
                                              LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(), True, {'key0': 'abc', 'key1': 'def'}),
            ({'key0': 100, 'key1': 200}, [LeafType(int, UnionTypeContext(is_dict=True)),
                                          LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(), True, {'key0': 100, 'key1': 200}),
            ({'key0': 100, 'key1': 'abc'}, [LeafType(int, UnionTypeContext(is_dict=True)),
                                            LeafType(str, UnionTypeContext(is_array=True))],
             UnionTypeContext(), False, None),

            # Partial Dictionary Cases
            ('abc', [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(), True, 'abc'),
            ({'key0': 100, 'key1': 200}, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(), True, {'key0': 100, 'key1': 200}),
            ({'key0': 100, 'key1': 'abc'}, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(), False, None),
            (100, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(), False, None),

            # Dictionary of Partial Dictionary Cases
            ({'key0': 'abc', 'key1': 'def'}, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(is_dict=True), True, {'key0': 'abc', 'key1': 'def'}),
            ({'key0': {'key0': 100, 'key1': 200}}, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(is_dict=True), True, {'key0': {'key0': 100, 'key1': 200}}),
            ({'key0': {'key0': 100, 'key1': 200}, 'key1': 'abc'},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(is_dict=True), True, {'key0': {'key0': 100, 'key1': 200}, 'key1': 'abc'}),
            ({'key0': {'key0': 100, 'key1': 'abc'}}, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': 100}, [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str)],
             UnionTypeContext(is_dict=True), False, None),

            # Dictionary of Dictionary Cases
            ({'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 'ghi', 'key1': 'jkl'}},
             [LeafType(int, UnionTypeContext(is_array=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 'ghi', 'key1': 'jkl'}}),
            ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 300, 'key1': 400}},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 300, 'key1': 400}}),
            ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}}),
            ({'key0': {'key0': 100, 'key1': 'abc'}, 'key1': {'key0': 200, 'key1': 'def'}},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': {'key0': 100, 'key1': 'abc'}, 'key1': {'key0': 'abc', 'key1': 'def'}},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': {'key0': 100.45, 'key1': 200.45}, 'key1': {'key0': 100, 'key1': 200}},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 100.45, 'key1': 200.45}},
             [LeafType(int, UnionTypeContext(is_dict=True)), LeafType(str, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), False, None),

            # Inner array of dictionary cases
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}],
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), True, [{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}]),
            ([{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}],
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), True, [{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}]),
            ([{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}],
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), False, None),
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), False, None),
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), False, None),
            ({'key0': 100, 'key1': 200},
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), False, None),

            # Outer array of dictionary cases
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}]),
            ([{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}]),
            ([{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}]),
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}]),
            ({'key0': 'abc', 'key1': 'def'},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), False,
             None),

            # dictionary of array cases
            ({'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']},
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), True, {'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']}),
            ({'key0': [100, 200], 'key1': [300, 400]},
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), True, {'key0': [100, 200], 'key1': [300, 400]}),
            ({'key0': ['abc', 200], 'key1': ['def', 400]},
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), False, None),
            ({'key0': [100, 200], 'key1': ['abc', 'def']},
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), False, None),
            ([{'key0': [100, 200]}, {'key1': ['abc', 'def']}],
             [LeafType(int, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(str, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), False, None),

            # Outer dictionary of array cases
            ({'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True, {'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']}),
            ({'key0': [100, 200], 'key1': [300, 400]},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True, {'key0': [100, 200], 'key1': [300, 400]}),
            ({'key0': ['abc', 200], 'key1': ['def', 400]},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True, {'key0': ['abc', 200], 'key1': ['def', 400]}),
            ({'key0': [100, 200], 'key1': ['abc', 'def']},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True, {'key0': [100, 200], 'key1': ['abc', 'def']}),
            ([{'key0': [100, 200]}, {'key1': ['abc', 'def']}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), False, None),

            # Nested oneOf cases
            ([[100, 200], ['abc', True]],
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_array=True)), LeafType(int, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[100, 200], ['abc', True]]),
            ([[100, 200], ['abc', True], None],
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_array=True, is_nullable=True)), LeafType(int, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[100, 200], ['abc', True], None]),
            ({'key0': {'key0': 100, 'key1': 200}, 'key2': {'key0': 'abc', 'key1': True}, 'key3': None},
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_dict=True, is_nullable=True)), LeafType(int, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': 100, 'key1': 200}, 'key2': {'key0': 'abc', 'key1': True}, 'key3': None}),
            ({'key0': [100, 200], 'key2': ['abc', True], 'key3': None},
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_array=True, is_nullable=True)), LeafType(int, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': [100, 200], 'key2': ['abc', True], 'key3': None}),
            ({'key0': [100, 200], 'key2': ['abc', True], 'key3': None},
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_array=True, is_nullable=True)), LeafType(int, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': [100, 200], 'key2': ['abc', True], 'key3': None}),
            ([{'key0': 100, 'key1': 200}, {'key0': 'abc', 'key1': True}, None],
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_dict=True, is_nullable=True)), LeafType(int, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_array=True, is_array_of_dict=True), True,
             [{'key0': 100, 'key1': 200}, {'key0': 'abc', 'key1': True}, None]),
            ([[100, 200], None],
             [OneOf([LeafType(str, UnionTypeContext()), LeafType(bool, UnionTypeContext())],
                    UnionTypeContext(is_array=True)), LeafType(int, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
        ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_one_of_primitive_type(
            self, input_value: Any, input_types: List[UnionType], input_context: UnionTypeContext,
            expected_is_valid_output: bool, expected_deserialized_value_output: Any
    ):
        try:
            union_type_result = OneOf(input_types, input_context).validate(input_value)
            actual_is_valid = union_type_result.is_valid
            actual_deserialized_value = union_type_result.deserialize(input_value)
        except OneOfValidationException:
            actual_is_valid = False
            actual_deserialized_value = None

        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output

    @pytest.mark.parametrize(
        'input_value, input_date, input_types, input_context, expected_validity, expected_value', [
            (Base.get_rfc3339_datetime(datetime(1994, 11, 6, 8, 49, 37), False),
             Base.get_rfc3339_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext(date_time_format=DateTimeFormat.RFC3339_DATE_TIME)),
              LeafType(date)], UnionTypeContext(), True, datetime(1994, 11, 6, 8, 49, 37)),
            (Base.get_http_datetime(datetime(1994, 11, 6, 8, 49, 37), False),
             Base.get_http_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext(date_time_format=DateTimeFormat.HTTP_DATE_TIME)), LeafType(date)],
             UnionTypeContext(), True, datetime(1994, 11, 6, 8, 49, 37)),
            (ApiHelper.UnixDateTime(datetime(1994, 11, 6, 8, 49, 37)), 1480809600,
             [LeafType(datetime, UnionTypeContext(date_time_format=DateTimeFormat.UNIX_DATE_TIME)), LeafType(date)],
             UnionTypeContext(), True, datetime.utcfromtimestamp(1480809600)),
            (datetime(1994, 11, 6, 8, 49, 37), Base.get_rfc3339_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext(date_time_converter=ApiHelper.RFC3339DateTime,
                                                  date_time_format=DateTimeFormat.RFC3339_DATE_TIME)), LeafType(date)],
             UnionTypeContext(), True, datetime(1994, 11, 6, 8, 49, 37)),
            ('1994-11-06', '1994-11-06',
             [LeafType(date), LeafType(datetime, UnionTypeContext(date_time_format=DateTimeFormat.RFC3339_DATE_TIME))],
             UnionTypeContext(),
             True, date(1994, 11, 6))
        ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_any_of_date_and_datetime(
            self, input_value: Any, input_date: Union[str, float, int], input_types: List[UnionType],
            input_context: UnionTypeContext, expected_validity: bool, expected_value: Union[date, datetime]
    ):
        union_type_result = OneOf(input_types, input_context).validate(input_value)

        assert union_type_result.is_valid == expected_validity
        actual_deserialized_value = union_type_result.deserialize(input_date)
        assert actual_deserialized_value == expected_value

    @pytest.mark.parametrize(
        'input_value, input_types, input_context, expected_validity, expected_value', [
            (None, [LeafType(int, UnionTypeContext(is_optional=True)), LeafType(str)], UnionTypeContext(), True, None),
            (None, [LeafType(int, UnionTypeContext(is_optional=True)), LeafType(str, UnionTypeContext(is_optional=True))],
             UnionTypeContext(), True, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext(is_nullable=True), True, None),
            (None, [LeafType(int, UnionTypeContext(is_nullable=True)), LeafType(str)], UnionTypeContext(), True, None),
            (None, [LeafType(int, UnionTypeContext(is_nullable=True)), LeafType(str, UnionTypeContext(is_optional=True))],
             UnionTypeContext(), True, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext(is_nullable=True), True, None),
            ([1, None, 2], [LeafType(int, UnionTypeContext(is_nullable=True)), LeafType(str)],
             UnionTypeContext(is_array=True), True, [1, None, 2]),
            ({'key0': 1, 'key3': 2}, [LeafType(int, UnionTypeContext(is_nullable=True)), LeafType(str)],
             UnionTypeContext(is_dict=True), True, {'key0': 1, 'key3': 2})
        ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_one_of_optional_nullable(
            self, input_value: Any, input_types: List[UnionType], input_context: UnionTypeContext,
            expected_validity: bool, expected_value: Any
    ):
        union_type_result = OneOf(input_types, input_context).validate(input_value)

        assert union_type_result.is_valid == expected_validity
        actual_deserialized_value = union_type_result.deserialize(input_value)
        assert actual_deserialized_value == expected_value

    @pytest.mark.parametrize(
        'input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output', [
            # Simple Cases
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(), True, Atom(atom_number_of_electrons=2, atom_number_of_protons=5)),
            ({"OrbitNumberOfElectrons": 4}, [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(), True, Orbit(orbit_number_of_electrons=4)),

            # Outer Array Cases
            ([{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext(is_array=True), True, [Orbit(orbit_number_of_electrons=4), Atom(atom_number_of_electrons=2, atom_number_of_protons=5)]),
            ([{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}],
            [LeafType(Atom), LeafType(Orbit)], UnionTypeContext(is_array=True), True, [Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=4, atom_number_of_protons=10)]),
            ([{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 5}],
             [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(is_array=True), True, [Orbit(orbit_number_of_electrons=4), Orbit(orbit_number_of_electrons=5)]),
            ({"OrbitNumberOfElectrons": 4},
             [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(is_array=True), False, None),
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
             [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(is_array=True), False, None),

            # Inner Array Cases
            ([{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(), False, None),
            ([{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}],
            [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
            UnionTypeContext(), True, [Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=4, atom_number_of_protons=10)]),
            ([{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 5}],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(), True, [Orbit(orbit_number_of_electrons=4), Orbit(orbit_number_of_electrons=5)]),
            ([{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(), False, None),
            ({"OrbitNumberOfElectrons": 4},
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(), False, None),
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(), False, None),

            # Partial Array Case
            ({"OrbitNumberOfElectrons": 4},
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext())], UnionTypeContext(), True, Orbit(orbit_number_of_electrons=4)),
            ([{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}],
            [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext())], UnionTypeContext(), True, [Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=4, atom_number_of_protons=10)]),
            ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext(), False, None),
            ('{"OrbitNumberOfElectrons": 4}', [LeafType(Orbit, UnionTypeContext(is_array=True)), LeafType(Atom)],
             UnionTypeContext(), False, None),

            # Array of Partial Arrays Cases
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit)],
             UnionTypeContext(is_array=True), True, [[Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=4, atom_number_of_protons=10)]]),
            ([[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 4}]],
             [LeafType(Orbit, UnionTypeContext(is_array=True)), LeafType(Atom)],
             UnionTypeContext(is_array=True), True, [[Orbit(orbit_number_of_electrons=4), Orbit(orbit_number_of_electrons=4)]]),
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}], {"OrbitNumberOfElectrons": 4}],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext(is_array=True), True, [[Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=4, atom_number_of_protons=10)], Orbit(orbit_number_of_electrons=4)]),
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"OrbitNumberOfElectrons": 4}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit)],
             UnionTypeContext(is_array=True), False, None),
            ([{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit)],
             UnionTypeContext(is_array=True), False, None),

            # Array of Arrays Cases
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 3, "AtomNumberOfProtons": 6}],
              [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               {"AtomNumberOfElectrons": 3, "AtomNumberOfProtons": 7}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)),
              LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=3, atom_number_of_protons=6)], [Atom(atom_number_of_electrons=2, atom_number_of_protons=10), Atom(atom_number_of_electrons=3, atom_number_of_protons=7)]]),
            ([[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 6}],
              [{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}]],
             [LeafType(Orbit, UnionTypeContext(is_array=True)), LeafType(Atom, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[Orbit(orbit_number_of_electrons=4), Orbit(orbit_number_of_electrons=6)], [Orbit(orbit_number_of_electrons=8), Orbit(orbit_number_of_electrons=10)]]),
            ([[{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}],
              [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}]],
             [LeafType(Orbit, UnionTypeContext(is_array=True)), LeafType(Atom, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), True, [[Orbit(orbit_number_of_electrons=8), Orbit(orbit_number_of_electrons=10)], [Atom(atom_number_of_electrons=2, atom_number_of_protons=5), Atom(atom_number_of_electrons=2, atom_number_of_protons=10)]]),
            ([[{"OrbitNumberOfElectrons": 8}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
              [{"OrbitNumberOfElectrons": 10}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
            ([[{"OrbitNumberOfElectrons": 8}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
              [{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
            ([[{"OrbitNumberOfElectrons": 8.5}, {"OrbitNumberOfElectrons": 10.5}],
              [{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),
            ([[{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10},
               {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}]],
             [LeafType(Atom, UnionTypeContext(is_array=True)), LeafType(Orbit, UnionTypeContext(is_array=True))],
             UnionTypeContext(is_array=True), False, None),

            # Outer Dictionary Cases
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext(is_dict=True), True,
             {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext(is_dict=True), True,
             {'key0': Orbit(orbit_number_of_electrons=8), 'key1': Orbit(orbit_number_of_electrons=10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key2': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Orbit), LeafType(Atom)], UnionTypeContext(is_dict=True), True,
             {'key0': Orbit(orbit_number_of_electrons=8), 'key2': Atom(atom_number_of_electrons=2, atom_number_of_protons=5)}),
            ({"OrbitNumberOfElectrons": 8}, [LeafType(Orbit), LeafType(Atom)], UnionTypeContext(is_dict=True), False, None),
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, [LeafType(Orbit), LeafType(Atom)],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}}},
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext(is_dict=True), False, None),

            # Inner Dictionary Cases
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(), True, {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(), True, {'key0': Orbit(orbit_number_of_electrons=8), 'key1': Orbit(orbit_number_of_electrons=10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)),
              LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(), False, None),

            # Partial Dictionary Cases
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, [LeafType(Orbit, UnionTypeContext(is_dict=True)),
                                                                      LeafType(Atom)], UnionTypeContext(), True,
             Atom(atom_number_of_electrons=2, atom_number_of_protons=5)),
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit)],
             UnionTypeContext(), True, {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}),
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, 'key1': {"OrbitNumberOfElectrons": 8}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit)], UnionTypeContext(), False, None),
            ({"OrbitNumberOfElectrons": 8}, [LeafType(Orbit, UnionTypeContext(is_dict=True)), LeafType(Atom)],
             UnionTypeContext(), False, None),

            # Dictionary of Partial Dictionary Cases
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit)],
             UnionTypeContext(is_dict=True), True, {'key0': Orbit(orbit_number_of_electrons=8), 'key1': Orbit(orbit_number_of_electrons=10)}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}}},
             [LeafType(Orbit, UnionTypeContext(is_dict=True)), LeafType(Atom)],
             UnionTypeContext(is_dict=True), True, {'key0': {'key0': Orbit(orbit_number_of_electrons=8), 'key1': Orbit(orbit_number_of_electrons=10)}}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Orbit, UnionTypeContext(is_dict=True)), LeafType(Atom)],
             UnionTypeContext(is_dict=True), True, {'key0': {'key0': Orbit(orbit_number_of_electrons=8), 'key1': Orbit(orbit_number_of_electrons=10)}, 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=5)}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 10},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}},
             [LeafType(Orbit, UnionTypeContext(is_dict=True)), LeafType(Atom)],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit)],
             UnionTypeContext(is_dict=True), False, None),

            # Dictionary of Dictionary Cases
            ({'key0': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
              'key1': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}, 'key1': {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 4}, 'key1': {"OrbitNumberOfElectrons": 8}},
              'key1': {'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}}},
             [LeafType(Orbit, UnionTypeContext(is_dict=True)), LeafType(Atom, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': Orbit(orbit_number_of_electrons=4), 'key1': Orbit(orbit_number_of_electrons=8)}, 'key1': {'key0': Orbit(orbit_number_of_electrons=10), 'key1': Orbit(orbit_number_of_electrons=12)}}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 8}},
              'key1': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), True,
             {'key0': {'key0': Orbit(orbit_number_of_electrons=10), 'key1': Orbit(orbit_number_of_electrons=8)}, 'key1': {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}}),
            ({'key0': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       'key1': {"OrbitNumberOfElectrons": 10}},
              'key1': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"OrbitNumberOfElectrons": 12}}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), False, None),
            ({'key0': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       'key1': {"OrbitNumberOfElectrons": 10}},
              'key1': {'key0': {"OrbitNumberOfElectrons": 12}, 'key1': {"OrbitNumberOfElectrons": 14}}},
             [LeafType(Atom, UnionTypeContext(is_dict=True)), LeafType(Orbit, UnionTypeContext(is_dict=True))],
             UnionTypeContext(is_dict=True), False, None),

            # Inner array of dictionary cases
            ([{'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}},
              {'key0': {"OrbitNumberOfElectrons": 14}, 'key1': {"OrbitNumberOfElectrons": 8}}],
             [LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), True,
             [{'key0': Orbit(orbit_number_of_electrons=10), 'key1': Orbit(orbit_number_of_electrons=12)}, {'key0': Orbit(orbit_number_of_electrons=14), 'key1': Orbit(orbit_number_of_electrons=8)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 15},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 20}}],
             [LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), True,
             [{'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=10)}, {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=15), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=20)}]),
            ([{'key0': {"OrbitNumberOfElectrons": 12}, 'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
              {'key0': {"OrbitNumberOfElectrons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 15}}],
             [LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), False, None),
            ([{'key0': {"OrbitNumberOfElectrons": 12}, 'key1': {"OrbitNumberOfElectrons": 10}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 20}}],
             [LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True)),
              LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True))],
             UnionTypeContext(), False, None),

            # Outer array of dictionary cases
            ([{'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}},
              {'key0': {"OrbitNumberOfElectrons": 14}, 'key1': {"OrbitNumberOfElectrons": 16}}],
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': Orbit(orbit_number_of_electrons=10), 'key1': Orbit(orbit_number_of_electrons=12)}, {'key0': Orbit(orbit_number_of_electrons=14), 'key1': Orbit(orbit_number_of_electrons=16)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 15}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 20},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}],
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=10), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=15)}, {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=20), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=5)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}, 'key1': {"OrbitNumberOfElectrons": 10}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               'key1': {"OrbitNumberOfElectrons": 12}}],
             [LeafType(Atom, UnionTypeContext()), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=10), 'key1': Orbit(orbit_number_of_electrons=10)}, {'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=5), 'key1': Orbit(orbit_number_of_electrons=12)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}},
              {'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}}],
             [LeafType(Atom, UnionTypeContext()), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True, is_array_of_dict=True), True,
             [{'key0': Atom(atom_number_of_electrons=2, atom_number_of_protons=10), 'key1': Atom(atom_number_of_electrons=2, atom_number_of_protons=12)}, {'key0': Orbit(orbit_number_of_electrons=10), 'key1': Orbit(orbit_number_of_electrons=12)}]),

            # dictionary of array cases
            ({'key0': [{"OrbitNumberOfElectrons": 10}, {"OrbitNumberOfElectrons": 12}],
              'key1': [{"OrbitNumberOfElectrons": 14}, {"OrbitNumberOfElectrons": 16}]},
             [LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), True, {'key0': [Orbit(orbit_number_of_electrons=10), Orbit(orbit_number_of_electrons=12)], 'key1': [Orbit(orbit_number_of_electrons=14), Orbit(orbit_number_of_electrons=16)]}),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}],
              'key1': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 14},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 16}]},
             [LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), True, {'key0': [Atom(atom_number_of_electrons=2, atom_number_of_protons=10), Atom(atom_number_of_electrons=2, atom_number_of_protons=12)], 'key1': [Atom(atom_number_of_electrons=2, atom_number_of_protons=14), Atom(atom_number_of_electrons=2, atom_number_of_protons=16)]}),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}, {"OrbitNumberOfElectrons": 10}],
              'key1': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}, {"OrbitNumberOfElectrons": 12}]},
             [LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), False, None),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}],
              'key1': [{"OrbitNumberOfElectrons": 10}, {"OrbitNumberOfElectrons": 12}]},
             [LeafType(Atom, UnionTypeContext(is_dict=True, is_array=True)),
              LeafType(Orbit, UnionTypeContext(is_dict=True, is_array=True))],
             UnionTypeContext(), False, None),

            # Outer dictionary of array cases
            ({'key0': [{"OrbitNumberOfElectrons": 10}, {"OrbitNumberOfElectrons": 12}],
              'key1': [{"OrbitNumberOfElectrons": 14}, {"OrbitNumberOfElectrons": 16}]},
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True,
             {'key0': [Orbit(orbit_number_of_electrons=10), Orbit(orbit_number_of_electrons=12)], 'key1': [Orbit(orbit_number_of_electrons=14), Orbit(orbit_number_of_electrons=16)]}),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}],
              'key1': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}]},
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True,
             {'key0': [Atom(atom_number_of_electrons=2, atom_number_of_protons=10), Atom(atom_number_of_electrons=2, atom_number_of_protons=12)], 'key1': [Atom(atom_number_of_electrons=2, atom_number_of_protons=10), Atom(atom_number_of_electrons=2, atom_number_of_protons=12)]}),
            ({'key0': [{"OrbitNumberOfElectrons": 10}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}],
              'key1': [{"OrbitNumberOfElectrons": 12}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}]},
             [LeafType(Atom, UnionTypeContext()), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext(is_dict=True, is_array=True), True,
             {'key0': [Orbit(orbit_number_of_electrons=10), Atom(atom_number_of_electrons=2, atom_number_of_protons=10)], 'key1': [Orbit(orbit_number_of_electrons=12), Atom(atom_number_of_electrons=2, atom_number_of_protons=12)]}),
        ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_one_of_custom_type(
            self, input_value: Any, input_types: List[UnionType], input_context: UnionTypeContext,
            expected_is_valid_output: bool, expected_deserialized_value_output: Any
    ):
        try:
            union_type_result = OneOf(input_types, input_context).validate(input_value)
            actual_is_valid = union_type_result.is_valid
            actual_deserialized_value = union_type_result.deserialize(input_value)
        except OneOfValidationException:
            actual_is_valid = False
            actual_deserialized_value = None

        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_output', [
        # Simple Cases
        ('{"id": "123", "weight": 5, "type": "lion", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"id": "123", "weight": 5, "type": "lion123", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer123", "kind": "hunted"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"id": "123", "weight": 5, "type": "lion", "kind": "hunter123"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunted123"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"id": "123", "weight": 5, "type": "lion", "kind": "hunter"}',
         [LeafType(Deer, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(Rabbit, UnionTypeContext(discriminator='type', discriminator_value='lion'))],
         UnionTypeContext(), False),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunted"}',
         [LeafType(Lion, UnionTypeContext(discriminator='type', discriminator_value='deer')),
          LeafType(Rabbit, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), False),

        ('{"id": "123", "weight": 5, "type": "lion", "kind": "hunter"}',
         [LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunter"}',
         [LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunter"}',
         [LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='deer')),
          LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='deer'))],
         UnionTypeContext(), False),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunter"}',
         [LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='lion')),
          LeafType(dict, UnionTypeContext(discriminator='type', discriminator_value='lion'))],
         UnionTypeContext(), False),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunter"}',
         [LeafType(dict), LeafType(dict)], UnionTypeContext(), False),
    ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_one_of_with_discriminator_custom_type(
            self, input_value: Any, input_types: List[UnionType], input_context: UnionTypeContext,
            expected_output: Any
    ):
        try:
            deserialized_dict_input = ApiHelper.json_deserialize(input_value, as_dict=True)
            union_type_result = OneOf(input_types, input_context).validate(deserialized_dict_input)
            actual_is_valid = union_type_result.is_valid
        except OneOfValidationException:
            actual_is_valid = False

        assert actual_is_valid == expected_output

    @pytest.mark.parametrize('input_value, input_types, input_context,  expected_is_valid_output, '
                             'expected_deserialized_value_output', [
        # Simple Cases
        ('Monday', [LeafType(Days, UnionTypeContext()), LeafType(Months, UnionTypeContext())],
         UnionTypeContext(), True, 'Monday'),
        (1, [LeafType(Days, UnionTypeContext()), LeafType(Months, UnionTypeContext())],
         UnionTypeContext(), True, 1),
        (0, [LeafType(Days, UnionTypeContext()), LeafType(Months, UnionTypeContext())],
         UnionTypeContext(), False, None),
        ('Monday_', [LeafType(Days, UnionTypeContext()), LeafType(Months, UnionTypeContext())],
         UnionTypeContext(), False, None),

        # Outer Array
        (['Monday', 'Tuesday'], [LeafType(Days), LeafType(Months)], UnionTypeContext(is_array=True), True,
         ['Monday', 'Tuesday']),
        ([1, 2], [LeafType(Days), LeafType(Months)], UnionTypeContext(is_array=True), True,
         [1, 2]),
        ([1, 'Monday'], [LeafType(Days), LeafType(Months)], UnionTypeContext(is_array=True), True, [1, 'Monday']),
        (2, [LeafType(Days), LeafType(Months)], UnionTypeContext(is_array=True), False, None),
        ('Monday', [LeafType(Days), LeafType(Months)], UnionTypeContext(is_array=True), False, None),
        ([['January', 'February']], [LeafType(int), LeafType(str)], UnionTypeContext(is_array=True), False, None),

        # Inner Array Cases
        (['Monday', 'Tuesday'], [LeafType(Days, UnionTypeContext(is_array=True)),
                          LeafType(Months, UnionTypeContext(is_array=True))],
         UnionTypeContext(), True, ['Monday', 'Tuesday']),
        ([1, 2], [LeafType(Days, UnionTypeContext(is_array=True)), LeafType(Months, UnionTypeContext(is_array=True))],
         UnionTypeContext(), True, [1, 2]),
        ([1, 'Monday'],
         [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days, UnionTypeContext(is_array=True))],
         UnionTypeContext(), False, None),

        # Partial Array Case
        ('Monday', [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(), True, 'Monday'),
        ([1, 2], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(), True, [1, 2]),
        ([1, 'Monday'], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(), False, None),
        (1, [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(), False, None),

        # Array of Partial Arrays Cases
        (['Monday', 'Tuesday'], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(is_array=True), True, ['Monday', 'Tuesday']),
        ([[1, 2]], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(is_array=True), True, [[1, 2]]),
        ([[1, 2], 'Monday'], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(is_array=True), True, [[1, 2], 'Monday']),
        ([[1, 'Monday']], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(is_array=True), False, None),
        ([1], [LeafType(Months, UnionTypeContext(is_array=True)), LeafType(Days)],
         UnionTypeContext(is_array=True), False, None),

        # Array of Arrays Cases
        ([['Monday', 'Tuesday'], ['Wednesday', 'Thursday']], [LeafType(Days, UnionTypeContext(is_array=True)),
                                            LeafType(Months, UnionTypeContext(is_array=True))],
         UnionTypeContext(is_array=True), True, [['Monday', 'Tuesday'], ['Wednesday', 'Thursday']]),
        ([[1, 2], [3, 4]], [LeafType(Months, UnionTypeContext(is_array=True)),
                                    LeafType(Days, UnionTypeContext(is_array=True))],
         UnionTypeContext(is_array=True), True, [[1, 2], [3, 4]]),
        ([[1, 2], ['Monday', 'Tuesday']], [LeafType(Months, UnionTypeContext(is_array=True)),
                                        LeafType(Days, UnionTypeContext(is_array=True))],
         UnionTypeContext(is_array=True), True, [[1, 2], ['Monday', 'Tuesday']]),
    ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_one_of_enum_type(
            self, input_value: Any, input_types: List[UnionType], input_context: UnionTypeContext,
            expected_is_valid_output: bool, expected_deserialized_value_output: Any
    ):
        try:
            union_type_result = OneOf(input_types, input_context).validate(input_value)
            actual_is_valid = union_type_result.is_valid
            actual_deserialized_value = union_type_result.deserialize(input_value)
        except OneOfValidationException:
            actual_is_valid = False
            actual_deserialized_value = None

        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_validation_message', [
            # Simple Cases
            (100, [LeafType(int), LeafType(int), LeafType(str)], UnionTypeContext(),
             '{} \nActual Value: 100\nExpected Type: One Of int, int, str.'.format(
                 UnionTypeHelper.MORE_THAN_1_MATCHED_ERROR_MESSAGE)),
            (100.5, [LeafType(int), LeafType(bool), LeafType(str)], UnionTypeContext(),
             '{} \nActual Value: 100.5\nExpected Type: One Of int, bool, str.'.format(
                 UnionTypeHelper.NONE_MATCHED_ERROR_MESSAGE)),
            (100.5, [LeafType(int), OneOf([LeafType(bool), LeafType(str)])], UnionTypeContext(),
             '{} \nActual Value: 100.5\nExpected Type: One Of int, bool, str.'.format(
                 UnionTypeHelper.NONE_MATCHED_ERROR_MESSAGE))
        ])
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def test_one_of_validation_errors(
            self, input_value: Any, input_types: List[UnionType], input_context: UnionTypeContext,
            expected_validation_message: str
    ):
        with pytest.raises(OneOfValidationException) as validation_error:
            OneOf(input_types, input_context).validate(input_value)

        assert validation_error.value.message == expected_validation_message
