from datetime import date
import datetime
import pytest
from apimatic_core.types.datetime_format import DateTimeFormat
from datetime import datetime
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.one_of import OneOf
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.mocks.models.atom import Atom
from tests.apimatic_core.mocks.models.orbit import Orbit


class TestOneOf:

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output', [
        # Simple Cases
        (100, [LeafType(int), LeafType(str)], UnionTypeContext(), True, 100),
        (100, [LeafType(int), LeafType(int), LeafType(str)], UnionTypeContext(), False, None),
        ('abc', [LeafType(int), LeafType(str)], UnionTypeContext(), True, 'abc'),
        (True, [LeafType(bool), LeafType(str)], UnionTypeContext(), True, True),
        (datetime.date(1994, 2, 13, 14, 1, 54), [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.RFC3339_DATE_TIME)), LeafType(bool)], UnionTypeContext(), True, "02/13/1994 14:01:54"),
        (datetime.date(1994, 11, 6, 8, 49, 37), [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.HTTP_DATE_TIME)), LeafType(bool)], UnionTypeContext(), True, "Sun, 06 Nov 1994 08:49:37 GMT"),
        (datetime.date(1994, 11, 6, 8, 49, 37), [LeafType(datetime, UnionTypeContext().date_time_format(DateTimeFormat.UNIX_DATE_TIME)), LeafType(bool)], UnionTypeContext(), True, 1484719381),
        (date(1994, 11, 6), [LeafType(date, UnionTypeContext()), LeafType(bool)], UnionTypeContext(), True, 1484719381),
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
        ([100, 'abc'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext(), True, [100, 'abc']),

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
        ({'key0': {'key0': 100, 'key1': 200}, 'key1': 'abc'}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
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
         UnionTypeContext().dict(True), True, {'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 300, 'key1': 400}}),
        ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), True, {'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}}),
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

    def test_one_of_primitive_type(self, input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output):
        union_type = OneOf(input_types, input_context)
        union_type_result = union_type.validate(input_value)
        actual_is_valid = union_type_result.is_valid
        actual_deserialized_value = union_type_result.deserialize(input_value)
        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output', [
        # Simple Cases
        ('{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}', [LeafType(Atom), LeafType(Orbit)],
         UnionTypeContext(), True, Atom(2, 5)),
        ('{"OrbitNumberOfElectrons": 4}', [LeafType(Atom), LeafType(Orbit)],
         UnionTypeContext(), True, Orbit(4)),
        ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
         [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().array(True), True, [Orbit(4), Atom(2, 5)]),
        ('[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, {"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
         [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
         UnionTypeContext(), True, [Atom(2, 5), Atom(4, 10)]),
        ('[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 5}]',
         [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
         UnionTypeContext(), True, [Orbit(4), Orbit(5)]),
        ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
         [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
         UnionTypeContext(), False, None),
        ('{"key0": {"OrbitNumberOfElectrons": 4}, "key1": {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}',
         [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().dict(True), True,
         {"key0": Orbit(4), "key1": Atom(2, 5)}),
    ])
    def test_one_of_custom_type(self, input_value, input_types, input_context, expected_is_valid_output, expected_deserialized_value_output):
        union_type = OneOf(input_types, input_context)
        deserialized_dict_input = ApiHelper.json_deserialize(input_value, as_dict=True)
        union_type_result = union_type.validate(deserialized_dict_input)
        actual_is_valid = union_type_result.is_valid
        actual_deserialized_value = union_type_result.deserialize(deserialized_dict_input)
        assert actual_is_valid == expected_is_valid_output
        assert actual_deserialized_value == expected_deserialized_value_output