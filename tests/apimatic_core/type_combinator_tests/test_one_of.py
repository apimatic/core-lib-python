from datetime import datetime, date
import pytest

from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.one_of import OneOf
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.base import Base
from tests.apimatic_core.mocks.models.atom import Atom
from tests.apimatic_core.mocks.models.deer import Deer
from tests.apimatic_core.mocks.models.lion import Lion
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
            (None, [LeafType(int), LeafType(str)], UnionTypeContext().nullable(True), True, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext().optional(True), True, None),
            (None, [LeafType(int), LeafType(str)], UnionTypeContext(), False, None),

            # Outer Array Cases
            (['abc', 'def'], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), True, ['abc', 'def']),
            ([100, 200], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), True, [100, 200]),
            ([100, 'abc'], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), True, [100, 'abc']),
            (100, [LeafType(int), LeafType(str)], UnionTypeContext().array(True), False, None),
            ('100', [LeafType(int), LeafType(str)], UnionTypeContext().array(True), False, None),
            ([['abc', 'def']], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), False, None),

            # Inner Array Cases
            (['abc', 'def'], [LeafType(int, UnionTypeContext().array(True)),
                              LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext(), True, ['abc', 'def']),
            ([100, 200], [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext(), True, [100, 200]),
            ([100, 'abc'],
             [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext(), False, None),

            # Partial Array Case
            ('abc', [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext(), True, 'abc'),
            ([100, 200], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext(), True, [100, 200]),
            ([100, 'abc'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext(), False, None),
            (100, [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext(), False, None),

            # Array of Partial Arrays Cases
            (['abc', 'def'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext().array(True), True, ['abc', 'def']),
            ([[100, 200]], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext().array(True), True, [[100, 200]]),
            ([[100, 200], 'abc'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext().array(True), True, [[100, 200], 'abc']),
            ([[100, 'abc']], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext().array(True), False, None),
            ([100], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
             UnionTypeContext().array(True), False, None),

            # Array of Arrays Cases
            ([['abc', 'def'], ['def', 'ghi']], [LeafType(int, UnionTypeContext().array(True)),
                                                LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), True, [['abc', 'def'], ['def', 'ghi']]),
            ([[100, 200], [300, 400]], [LeafType(int, UnionTypeContext().array(True)),
                                        LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), True, [[100, 200], [300, 400]]),
            ([[100, 200], ['abc', 'def']], [LeafType(int, UnionTypeContext().array(True)),
                                            LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), True, [[100, 200], ['abc', 'def']]),
            ([[100, 'abc'], [200, 'def']], [LeafType(int, UnionTypeContext().array(True)),
                                            LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),
            ([[100, 'abc'], ['def', 'ghi']], [LeafType(int, UnionTypeContext().array(True)),
                                              LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),
            ([[100.45, 200.45], [100, 200]], [LeafType(int, UnionTypeContext().array(True)),
                                              LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),
            ([['abc', 'def'], [100.45, 200.45]], [LeafType(int, UnionTypeContext().array(True)),
                                                  LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),

            # Outer Dictionary Cases
            ({'key0': 'abc', 'key1': 'def'}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), True,
             {'key0': 'abc', 'key1': 'def'}),
            ({'key0': 100, 'key1': 200}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), True,
             {'key0': 100, 'key1': 200}),
            ({'key0': 100, 'key2': 'abc'}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), True,
             {'key0': 100, 'key2': 'abc'}),
            (100, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), False, None),
            ('100', [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), False, None),
            ({'key0': {'key0': 'abc', 'key1': 'def'}}, [LeafType(int), LeafType(str)],
             UnionTypeContext().dict(True), False, None),

            # Inner Dictionary Cases
            ({'key0': 'abc', 'key1': 'def'}, [LeafType(int, UnionTypeContext().dict(True)),
                                              LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext(), True, {'key0': 'abc', 'key1': 'def'}),
            ({'key0': 100, 'key1': 200}, [LeafType(int, UnionTypeContext().dict(True)),
                                          LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext(), True, {'key0': 100, 'key1': 200}),
            ({'key0': 100, 'key1': 'abc'}, [LeafType(int, UnionTypeContext().dict(True)),
                                            LeafType(str, UnionTypeContext().array(True))],
             UnionTypeContext(), False, None),

            # Partial Dictionary Cases
            ('abc', [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext(), True, 'abc'),
            ({'key0': 100, 'key1': 200}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext(), True, {'key0': 100, 'key1': 200}),
            ({'key0': 100, 'key1': 'abc'}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext(), False, None),
            (100, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext(), False, None),

            # Dictionary of Partial Dictionary Cases
            ({'key0': 'abc', 'key1': 'def'}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext().dict(True), True, {'key0': 'abc', 'key1': 'def'}),
            ({'key0': {'key0': 100, 'key1': 200}}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext().dict(True), True, {'key0': {'key0': 100, 'key1': 200}}),
            ({'key0': {'key0': 100, 'key1': 200}, 'key1': 'abc'},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext().dict(True), True, {'key0': {'key0': 100, 'key1': 200}, 'key1': 'abc'}),
            ({'key0': {'key0': 100, 'key1': 'abc'}}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext().dict(True), False, None),
            ({'key0': 100}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
             UnionTypeContext().dict(True), False, None),

            # Dictionary of Dictionary Cases
            ({'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 'ghi', 'key1': 'jkl'}},
             [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), True,
             {'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 'ghi', 'key1': 'jkl'}}),
            ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 300, 'key1': 400}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), True,
             {'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 300, 'key1': 400}}),
            ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), True,
             {'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}}),
            ({'key0': {'key0': 100, 'key1': 'abc'}, 'key1': {'key0': 200, 'key1': 'def'}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), False, None),
            ({'key0': {'key0': 100, 'key1': 'abc'}, 'key1': {'key0': 'abc', 'key1': 'def'}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), False, None),
            ({'key0': {'key0': 100.45, 'key1': 200.45}, 'key1': {'key0': 100, 'key1': 200}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), False, None),
            ({'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 100.45, 'key1': 200.45}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), False, None),

            # Inner array of dictionary cases
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}],
             [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), True, [{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}]),
            ([{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}],
             [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), True, [{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}]),
            ([{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}],
             [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), False, None),
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
             [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), False, None),
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
             [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), False, None),

            # Outer array of dictionary cases
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}]),
            ([{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}]),
            ([{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}]),
            ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}]),

            # dictionary of array cases
            ({'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']},
             [LeafType(int, UnionTypeContext().dict(True).array(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), True, {'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']}),
            ({'key0': [100, 200], 'key1': [300, 400]},
             [LeafType(int, UnionTypeContext().dict(True).array(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), True, {'key0': [100, 200], 'key1': [300, 400]}),
            ({'key0': ['abc', 200], 'key1': ['def', 400]},
             [LeafType(int, UnionTypeContext().dict(True).array(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), False, None),
            ({'key0': [100, 200], 'key1': ['abc', 'def']},
             [LeafType(int, UnionTypeContext().dict(True).array(True)),
              LeafType(str, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), False, None),

            # Outer dictionary of array cases
            ({'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True, {'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']}),
            ({'key0': [100, 200], 'key1': [300, 400]},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True, {'key0': [100, 200], 'key1': [300, 400]}),
            ({'key0': ['abc', 200], 'key1': ['def', 400]},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True, {'key0': ['abc', 200], 'key1': ['def', 400]}),
            ({'key0': [100, 200], 'key1': ['abc', 'def']},
             [LeafType(int, UnionTypeContext()), LeafType(str, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True, {'key0': [100, 200], 'key1': ['abc', 'def']}),
        ])
    def test_one_of_primitive_type(self, input_value, input_types, input_context, expected_is_valid_output,
                                   expected_deserialized_value_output):
        union_type = OneOf(input_types, input_context)
        union_type_result = union_type.validate(input_value)
        actual_is_valid = union_type_result.is_valid
        actual_deserialized_value = union_type_result.deserialize(input_value)
        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output

    @pytest.mark.parametrize(
        'input_value, input_types, input_context, expected_validity', [
            (Base.get_rfc3339_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.RFC3339_DATE_TIME)),
              LeafType(bool)], UnionTypeContext(), True),
            (Base.get_http_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.HTTP_DATE_TIME)), LeafType(bool)],
             UnionTypeContext(), True),
            (1480809600,
             [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.UNIX_DATE_TIME)), LeafType(bool)],
             UnionTypeContext(), True),
            (date(1994, 11, 6), [LeafType(date), LeafType(bool)], UnionTypeContext(), True)
        ])
    def test_one_of_date_and_datetime_validity(self, input_value, input_types, input_context, expected_validity):
        union_type = OneOf(input_types, input_context)
        union_type_result = union_type.validate(input_value)
        assert union_type_result.is_valid == expected_validity

    @pytest.mark.parametrize(
        'input_value, input_types, input_context, expected_value, expected_type', [
            (Base.get_rfc3339_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.RFC3339_DATE_TIME)),
              LeafType(bool)], UnionTypeContext(), datetime(1994, 11, 6, 8, 49, 37), datetime),
            (Base.get_http_datetime(datetime(1994, 11, 6, 8, 49, 37)),
             [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.HTTP_DATE_TIME)), LeafType(bool)],
             UnionTypeContext(), datetime(1994, 11, 6, 8, 49, 37), datetime),
            (1480809600,
             [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.UNIX_DATE_TIME)), LeafType(bool)],
             UnionTypeContext(), datetime.utcfromtimestamp(1480809600), datetime),
            ('1994-11-06', [LeafType(date), LeafType(bool)], UnionTypeContext(), date(1994, 11, 6), date)
        ])
    def test_one_of_date_and_datetime(self, input_value, input_types, input_context, expected_value, expected_type):
        union_type = OneOf(input_types, input_context)
        union_type_result = union_type.validate(input_value)
        actual_deserialized_value = union_type_result.deserialize(input_value)
        assert isinstance(actual_deserialized_value, expected_type)
        assert actual_deserialized_value == expected_value

    @pytest.mark.parametrize(
        'input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output', [
            # Simple Cases
            ('{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}', [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(), True, Atom(2, 5)),
            ('{"OrbitNumberOfElectrons": 4}', [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext(), True, Orbit(4)),
            ('{"key0": {"OrbitNumberOfElectrons": 4}, "key1": {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}',
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().dict(True), True,
             {"key0": Orbit(4), "key1": Atom(2, 5)}),

            # Outer Array Cases
            ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().array(True), True, [Orbit(4), Atom(2, 5)]),
            (
            '[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
            [LeafType(Atom), LeafType(Orbit)],
            UnionTypeContext().array(True), True, [Atom(2, 5), Atom(4, 10)]),
            ('[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 5}]',
             [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext().array(True), True, [Orbit(4), Orbit(5)]),
            ('{"OrbitNumberOfElectrons": 4}',
             [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext().array(True), False, None),
            ('{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}',
             [LeafType(Atom), LeafType(Orbit)],
             UnionTypeContext().array(True), False, None),

            # Inner Array Cases
            ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext(), False, None),
            (
            '[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
            [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
            UnionTypeContext(), True, [Atom(2, 5), Atom(4, 10)]),
            ('[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 5}]',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext(), True, [Orbit(4), Orbit(5)]),
            ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext(), False, None),
            ('{"OrbitNumberOfElectrons": 4}',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext(), False, None),
            ('{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext(), False, None),

            # Partial Array Case
            ('{"OrbitNumberOfElectrons": 4}',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)], UnionTypeContext(), True, Orbit(4)),
            (
            '[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
            [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)],
            UnionTypeContext(), True, [Atom(2, 5), Atom(4, 10)]),
            ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)],
             UnionTypeContext(), False, None),
            ('{"OrbitNumberOfElectrons": 4}', [LeafType(Orbit, UnionTypeContext().array(True)), LeafType(Atom)],
             UnionTypeContext(), False, None),

            # Array of Partial Arrays Cases
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)],
             UnionTypeContext().array(True), True, [[Atom(2, 5), Atom(4, 10)]]),
            ([[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 4}]],
             [LeafType(Orbit, UnionTypeContext().array(True)), LeafType(Atom)],
             UnionTypeContext().array(True), True, [[Orbit(4), Orbit(4)]]),
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}, {"OrbitNumberOfElectrons": 4}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)],
             UnionTypeContext().array(True), True, [Atom(2, 5), Orbit(4)]),
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"OrbitNumberOfElectrons": 4}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)],
             UnionTypeContext().array(True), False, None),
            ([{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit)],
             UnionTypeContext().array(True), False, None),

            # Array of Arrays Cases
            ([[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 3, "AtomNumberOfProtons": 6}],
              [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               {"AtomNumberOfElectrons": 3, "AtomNumberOfProtons": 7}]],
             [LeafType(Atom, UnionTypeContext().array(True)),
              LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), True, [[Atom(2, 5), Atom(3, 6)], [Atom(2, 10), Atom(3, 7)]]),
            ([[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 6}],
              [{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}]],
             [LeafType(Orbit, UnionTypeContext().array(True)), LeafType(Atom, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), True, [[Orbit(4), Orbit(6)], [Orbit(8), Orbit(10)]]),
            ([[{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}],
              [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}]],
             [LeafType(Orbit, UnionTypeContext().array(True)), LeafType(Atom, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), True, [[Orbit(8), Orbit(10)], [Atom(2, 5), Atom(2, 10)]]),
            ([[{"OrbitNumberOfElectrons": 8}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
              [{"OrbitNumberOfElectrons": 10}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),
            ([[{"OrbitNumberOfElectrons": 8}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}],
              [{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),
            ([[{"OrbitNumberOfElectrons": 8.5}, {"OrbitNumberOfElectrons": 10.5}],
              [{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),
            ([[{"OrbitNumberOfElectrons": 8}, {"OrbitNumberOfElectrons": 10}],
              [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}]],
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
             UnionTypeContext().array(True), False, None),

            # Outer Dictionary Cases
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().dict(True), True,
             {'key0': Atom(2, 5), 'key1': Atom(2, 10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().dict(True), True,
             {'key0': Orbit(8), 'key1': Orbit(10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key2': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Orbit), LeafType(Atom)], UnionTypeContext().dict(True), True,
             {'key0': Orbit(8), 'key2': Atom(2, 5)}),
            ({"OrbitNumberOfElectrons": 8}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), False, None),
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, [LeafType(int), LeafType(str)],
             UnionTypeContext().dict(True), False, None),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}}},
             [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().dict(True), False, None),

            # Inner Dictionary Cases
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
             [LeafType(Atom, UnionTypeContext().dict(True)), LeafType(Orbit, UnionTypeContext().dict(True))],
             UnionTypeContext(), True, {'key0': Atom(2, 5), 'key1': Atom(2, 10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext(), True, {'key0': Orbit(8), 'key1': Orbit(10)}),
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(int, UnionTypeContext().dict(True)),
              LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext(), False, None),

            # Partial Dictionary Cases
            ({"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, [LeafType(Orbit, UnionTypeContext().dict(True)),
                                                                      LeafType(Atom)], UnionTypeContext(), True,
             Atom(2, 5)),
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
             [LeafType(Atom, UnionTypeContext().dict(True)), LeafType(Orbit)],
             UnionTypeContext(), True, {'key0': Atom(2, 5), 'key1': Atom(2, 10)}),
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, 'key1': {"OrbitNumberOfElectrons": 8}},
             [LeafType(Atom, UnionTypeContext().dict(True)), LeafType(Orbit)], UnionTypeContext(), False, None),
            ({"OrbitNumberOfElectrons": 8}, [LeafType(Orbit, UnionTypeContext().dict(True)), LeafType(Atom)],
             UnionTypeContext(), False, None),

            # Dictionary of Partial Dictionary Cases
            ({'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
             [LeafType(Orbit, UnionTypeContext().dict(True)), LeafType(Atom)],
             UnionTypeContext().dict(True), True, {'key0': Orbit(8), 'key1': Orbit(10)}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}}},
             [LeafType(Orbit, UnionTypeContext().dict(True)), LeafType(Atom)],
             UnionTypeContext().dict(True), True, {'key0': {'key0': Orbit(8), 'key1': Orbit(10)}}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 8}, 'key1': {"OrbitNumberOfElectrons": 10}},
              'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Orbit, UnionTypeContext().dict(True)), LeafType(Atom)],
             UnionTypeContext().dict(True), True, {'key0': {'key0': Orbit(8), 'key1': Orbit(10)}, 'key1': Atom(2, 5)}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 10},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}},
             [LeafType(Orbit, UnionTypeContext().dict(True)), LeafType(Atom)],
             UnionTypeContext().dict(True), False, None),
            ({'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}},
             [LeafType(Atom, UnionTypeContext().dict(True)), LeafType(Orbit)],
             UnionTypeContext().dict(True), False, None),

            # Dictionary of Dictionary Cases
            ({'key0': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}}, \
              'key1': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, \
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}}},
             [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), True,
             {'key0': {'key0': Atom(2, 5), 'key1': Atom(2, 10)}, 'key1': {'key0': Atom(2, 5), 'key1': Atom(2, 10)}}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 4}, 'key1': {"OrbitNumberOfElectrons": 8}},
              'key1': {'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}}},
             [LeafType(Orbit, UnionTypeContext().dict(True)), LeafType(Atom, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), True,
             {'key0': {'key0': Orbit(4), 'key1': Orbit(8)}, 'key1': {'key0': Orbit(10), 'key1': Orbit(12)}}),
            ({'key0': {'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 8}},
              'key1': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}}},
             [LeafType(Atom, UnionTypeContext().dict(True)), LeafType(Orbit, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), True,
             {'key0': {'key0': Atom(2, 5), 'key1': Atom(2, 10)}, 'key1': {'key0': Orbit(10), 'key1': Orbit(8)}}),
            ({'key0': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       'key1': {"OrbitNumberOfElectrons": 10}},
              'key1': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
                       'key1': {"OrbitNumberOfElectrons": 12}}},
             [LeafType(Atom, UnionTypeContext().dict(True)), LeafType(Orbit, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), False, None),
            ({'key0': {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       'key1': {"OrbitNumberOfElectrons": 10}},
              'key1': {'key0': {"OrbitNumberOfElectrons": 12}, 'key1': {"OrbitNumberOfElectrons": 14}}},
             [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
             UnionTypeContext().dict(True), False, None),

            # Inner array of dictionary cases
            ([{'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}},
              {'key0': {"OrbitNumberOfElectrons": 14}, 'key1': {"OrbitNumberOfElectrons": 8}}],
             [LeafType(Orbit, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(Atom, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), True,
             [{'key0': Orbit(10), 'key1': Orbit(12)}, {'key0': Orbit(14), 'key1': Orbit(8)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 15},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 20}}],
             [LeafType(Atom, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(Orbit, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), True,
             [{'key0': Atom(2, 5), 'key1': Atom(2, 10)}, {'key0': Atom(2, 15), 'key1': Atom(2, 20)}]),
            ([{'key0': {"OrbitNumberOfElectrons": 12}, 'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}},
              {'key0': {"OrbitNumberOfElectrons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 15}}],
             [LeafType(Orbit, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(Atom, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), False, None),
            ([{'key0': {"OrbitNumberOfElectrons": 12}, 'key1': {"OrbitNumberOfElectrons": 10}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 20}}],
             [LeafType(Orbit, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
              LeafType(Atom, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
             UnionTypeContext(), False, None),

            # Outer array of dictionary cases
            ([{'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}},
              {'key0': {"OrbitNumberOfElectrons": 14}, 'key1': {"OrbitNumberOfElectrons": 16}}],
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': Orbit(10), 'key1': Orbit(12)}, {'key0': Orbit(14), 'key1': Orbit(16)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 15}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 20},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}],
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': Atom(2, 10), 'key1': Atom(2, 15)}, {'key0': Atom(2, 20), 'key1': Atom(2, 5)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}, 'key1': {"OrbitNumberOfElectrons": 10}},
              {'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"OrbitNumberOfElectrons": 12}}],
             [LeafType(Atom, UnionTypeContext()), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': Atom(2, 10), 'key1': Orbit(10)}, {'key0': Atom(2, 5), 'key1': Orbit(12)}]),
            ([{'key0': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
               'key1': {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}},
              {'key0': {"OrbitNumberOfElectrons": 10}, 'key1': {"OrbitNumberOfElectrons": 12}}],
             [LeafType(Atom, UnionTypeContext()), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True).array_of_dict(True), True,
             [{'key0': Atom(2, 10), 'key1': Atom(2, 12)}, {'key0': Orbit(10), 'key1': Orbit(12)}]),

            # dictionary of array cases
            ({'key0': [{"OrbitNumberOfElectrons": 10}, {"OrbitNumberOfElectrons": 12}],
              'key1': [{"OrbitNumberOfElectrons": 14}, {"OrbitNumberOfElectrons": 16}]},
             [LeafType(Orbit, UnionTypeContext().dict(True).array(True)),
              LeafType(Atom, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), True, {'key0': [Orbit(10), Orbit(12)], 'key1': [Orbit(14), Orbit(16)]}),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}],
              'key1': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 14},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 16}]},
             [LeafType(Atom, UnionTypeContext().dict(True).array(True)),
              LeafType(Orbit, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), True, {'key0': [Atom(2, 10), Atom(2, 12)], 'key1': [Atom(2, 14), Atom(2, 16)]}),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}, {"OrbitNumberOfElectrons": 10}],
              'key1': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}, {"OrbitNumberOfElectrons": 12}]},
             [LeafType(Atom, UnionTypeContext().dict(True).array(True)),
              LeafType(Orbit, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), False, None),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}],
              'key1': [{"OrbitNumberOfElectrons": 10}, {"OrbitNumberOfElectrons": 12}]},
             [LeafType(Atom, UnionTypeContext().dict(True).array(True)),
              LeafType(Orbit, UnionTypeContext().dict(True).array(True))],
             UnionTypeContext(), False, None),

            # Outer dictionary of array cases
            ({'key0': [{"OrbitNumberOfElectrons": 10}, {"OrbitNumberOfElectrons": 12}],
              'key1': [{"OrbitNumberOfElectrons": 14}, {"OrbitNumberOfElectrons": 16}]},
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True,
             {'key0': [Orbit(10), Orbit(12)], 'key1': [Orbit(14), Orbit(16)]}),
            ({'key0': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}],
              'key1': [{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10},
                       {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}]},
             [LeafType(Orbit, UnionTypeContext()), LeafType(Atom, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True,
             {'key0': [Atom(2, 10), Atom(2, 12)], 'key1': [Atom(2, 10), Atom(2, 12)]}),
            ({'key0': [{"OrbitNumberOfElectrons": 10}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 10}],
              'key1': [{"OrbitNumberOfElectrons": 12}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 12}]},
             [LeafType(Atom, UnionTypeContext()), LeafType(Orbit, UnionTypeContext())],
             UnionTypeContext().dict(True).array(True), True,
             {'key0': [Orbit(10), Atom(2, 10)], 'key1': [Orbit(12), Atom(2, 12)]}),
        ])
    def test_one_of_custom_type(self, input_value, input_types, input_context, expected_is_valid_output,
                                expected_deserialized_value_output):
        union_type = OneOf(input_types, input_context)
        deserialized_dict_input = ApiHelper.json_deserialize(input_value, as_dict=True)
        union_type_result = union_type.validate(deserialized_dict_input)
        actual_is_valid = union_type_result.is_valid
        actual_deserialized_value = union_type_result.deserialize(deserialized_dict_input)
        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_output', [
        # Simple Cases
        ('{"id": 123, "weight": 5, "type": "lion", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Deer, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Deer, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), True),
        ('{"id": 123, "weight": 5, "type": "lion123", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Deer, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer123", "kind": "hunted"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Deer, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), True),
        ('{"id": 123, "weight": 5, "type": "lion", "kind": "hunter123"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Deer, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), True),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunted123"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Deer, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), True),
        ('{"id": 123, "weight": 5, "type": "lion", "kind": "hunter"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('lion')),
          LeafType(Rabbit, UnionTypeContext().discriminator('type').discriminator_value('lion'))],
         UnionTypeContext(), False),
        ('{"name": "sam", "weight": 5, "type": "deer", "kind": "hunted"}',
         [LeafType(Lion, UnionTypeContext().discriminator('type').discriminator_value('deer')),
          LeafType(Rabbit, UnionTypeContext().discriminator('type').discriminator_value('deer'))],
         UnionTypeContext(), False)
    ])
    def test_one_of_custom_type(self, input_value, input_types, input_context, expected_output):
        union_type = OneOf(input_types, input_context)
        deserialized_dict_input = ApiHelper.json_deserialize(input_value, as_dict=True)
        union_type_result = union_type.validate(deserialized_dict_input)
        actual_result = union_type_result.is_valid
        deserialized_value = union_type_result.deserialize(deserialized_dict_input)
        assert actual_result == expected_output