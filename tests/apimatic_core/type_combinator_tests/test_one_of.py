import dateutil
import pytest

from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.one_of import OneOf
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.mocks.models.atom import Atom
from tests.apimatic_core.mocks.models.orbit import Orbit


class TestOneOf:

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_output', [
        # Simple Cases
        (100, [LeafType(int), LeafType(str)], UnionTypeContext(), True),
        (100, [LeafType(int), LeafType(int), LeafType(str)], UnionTypeContext(), False),
        ('abc', [LeafType(int), LeafType(str)], UnionTypeContext(), True),
        (100.44, [LeafType(int), LeafType(str)], UnionTypeContext(), False),

        # Outer Array Cases
        (['abc', 'def'], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), True),
        ([100, 200], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), True),
        ([100, 'abc'], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), True),
        (100, [LeafType(int), LeafType(str)], UnionTypeContext().array(True), False),
        ('100', [LeafType(int), LeafType(str)], UnionTypeContext().array(True), False),
        ([['abc', 'def']], [LeafType(int), LeafType(str)], UnionTypeContext().array(True), False),

        # Inner Array Cases
        (['abc', 'def'], [LeafType(int, UnionTypeContext().array(True)),
                          LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext(), True),
        ([100, 200], [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext(), True),
        ([100, 'abc'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext(), False),

        # Partial Array Case
        ('abc', [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext(), True),
        ([100, 200], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext(), True),
        ([100, 'abc'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext(), False),
        (100, [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext(), False),

        # Array of Partial Arrays Cases
        (['abc', 'def'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext().array(True), True),
        ([[100, 200]], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext().array(True), True),
        ([[100, 200], 'abc'], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext().array(True), True),
        ([[100, 'abc']], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext().array(True), False),
        ([100], [LeafType(int, UnionTypeContext().array(True)), LeafType(str)],
         UnionTypeContext().array(True), False),

        # Array of Arrays Cases
        ([['abc', 'def'], ['def', 'ghi']], [LeafType(int, UnionTypeContext().array(True)),
                                            LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), True),
        ([[100, 200], [300, 400]], [LeafType(int, UnionTypeContext().array(True)),
                                    LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), True),
        ([[100, 200], ['abc', 'def']], [LeafType(int, UnionTypeContext().array(True)),
                                        LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), True),
        ([[100, 'abc'], [200, 'def']], [LeafType(int, UnionTypeContext().array(True)),
                                        LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), False),
        ([[100, 'abc'], ['def', 'ghi']], [LeafType(int, UnionTypeContext().array(True)),
                                          LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), False),
        ([[100.45, 200.45], [100, 200]], [LeafType(int, UnionTypeContext().array(True)),
                                          LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), False),
        ([['abc', 'def'], [100.45, 200.45]], [LeafType(int, UnionTypeContext().array(True)),
                                              LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext().array(True), False),

        # Outer Dictionary Cases
        ({'key0': 'abc', 'key1': 'def'}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), True),
        ({'key0': 100, 'key1': 200}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), True),
        ({'key0': 100, 'key2': 'abc'}, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), True),
        (100, [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), False),
        ('100', [LeafType(int), LeafType(str)], UnionTypeContext().dict(True), False),
        ({'key0': {'key0': 'abc', 'key1': 'def'}}, [LeafType(int), LeafType(str)],
         UnionTypeContext().dict(True), False),

        # Inner Dictionary Cases
        ({'key0': 'abc', 'key1': 'def'}, [LeafType(int, UnionTypeContext().dict(True)),
                                          LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext(), True),
        ({'key0': 100, 'key1': 200}, [LeafType(int, UnionTypeContext().dict(True)),
                                      LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext(), True),
        ({'key0': 100, 'key1': 'abc'}, [LeafType(int, UnionTypeContext().dict(True)),
                                        LeafType(str, UnionTypeContext().array(True))],
         UnionTypeContext(), False),

        # Partial Dictionary Cases
        ('abc', [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext(), True),
        ({'key0': 100, 'key1': 200}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext(), True),
        ({'key0': 100, 'key1': 'abc'}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext(), False),
        (100, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext(), False),

        # Dictionary of Partial Dictionary Cases
        ({'key0': 'abc', 'key1': 'def'}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext().dict(True), True),
        ({'key0': {'key0': 100, 'key1': 200}}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext().dict(True), True),
        ({'key0': {'key0': 100, 'key1': 200}, 'key1': 'abc'}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext().dict(True), True),
        ({'key0': {'key0': 100, 'key1': 'abc'}}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext().dict(True), False),
        ({'key0': 100}, [LeafType(int, UnionTypeContext().dict(True)), LeafType(str)],
         UnionTypeContext().dict(True), False),

        # Dictionary of Dictionary Cases
        ({'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 'ghi', 'key1': 'jkl'}},
         [LeafType(int, UnionTypeContext().array(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), True),
        ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 300, 'key1': 400}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), True),
        ({'key0': {'key0': 100, 'key1': 200}, 'key1': {'key0': 'abc', 'key1': 'def'}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), True),
        ({'key0': {'key0': 100, 'key1': 'abc'}, 'key1': {'key0': 200, 'key1': 'def'}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), False),
        ({'key0': {'key0': 100, 'key1': 'abc'}, 'key1': {'key0': 'abc', 'key1': 'def'}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), False),
        ({'key0': {'key0': 100.45, 'key1': 200.45}, 'key1': {'key0': 100, 'key1': 200}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), False),
        ({'key0': {'key0': 'abc', 'key1': 'def'}, 'key1': {'key0': 100.45, 'key1': 200.45}},
         [LeafType(int, UnionTypeContext().dict(True)), LeafType(str, UnionTypeContext().dict(True))],
         UnionTypeContext().dict(True), False),

        # array of dictionary cases
        ([{'key0': 'abc', 'key1': 'def'}, {'key0': 'ghi', 'key1': 'jkl'}],
         [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
         UnionTypeContext(), True),
        ([{'key0': 100, 'key1': 200}, {'key0': 300, 'key1': 400}],
         [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
         UnionTypeContext(), True),
        ([{'key0': 'abc', 'key1': 200}, {'key0': 'def', 'key1': 400}],
         [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
         UnionTypeContext(), False),
        ([{'key0': 'abc', 'key1': 'def'}, {'key0': 100, 'key1': 200}],
         [LeafType(int, UnionTypeContext().dict(True).array(True).array_of_dict(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True).array_of_dict(True))],
         UnionTypeContext(), False),

        # dictionary of array cases
        ({'key0': ['abc', 'def'], 'key1': ['ghi', 'jkl']},
         [LeafType(int, UnionTypeContext().dict(True).array(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True))],
         UnionTypeContext(), True),
        ({'key0': [100, 200], 'key1': [300, 400]},
         [LeafType(int, UnionTypeContext().dict(True).array(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True))],
         UnionTypeContext(), True),
        ({'key0': ['abc', 200], 'key1': ['def', 400]},
         [LeafType(int, UnionTypeContext().dict(True).array(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True))],
         UnionTypeContext(), False),
        ({'key0': [100, 200], 'key1': ['abc', 'def']},
         [LeafType(int, UnionTypeContext().dict(True).array(True)),
          LeafType(str, UnionTypeContext().dict(True).array(True))],
         UnionTypeContext(), False),
    ])
    def test_one_of_primitive_type(self, input_value, input_types, input_context, expected_output):
        union_type = OneOf(input_types, input_context)
        union_type_result = union_type.validate(input_value)
        actual_result = union_type_result.is_valid
        deserialized_value = union_type_result.deserialize(input_value)
        assert actual_result == expected_output

    @pytest.mark.parametrize('input_value, input_types, input_context, expected_output', [
        # Simple Cases
        ('{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}', [LeafType(Atom), LeafType(Orbit)],
         UnionTypeContext(), True),
        ('{"OrbitNumberOfElectrons": 4}', [LeafType(Atom), LeafType(Orbit)],
         UnionTypeContext(), True),
        ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
         [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().array(True), True),
        ('[{"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}, '
         '{"AtomNumberOfElectrons": 4, "AtomNumberOfProtons": 10}]',
         [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
         UnionTypeContext(), True),
        ('[{"OrbitNumberOfElectrons": 4}, {"OrbitNumberOfElectrons": 5}]',
         [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
         UnionTypeContext(), True),
        ('[{"OrbitNumberOfElectrons": 4}, {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}]',
         [LeafType(Atom, UnionTypeContext().array(True)), LeafType(Orbit, UnionTypeContext().array(True))],
         UnionTypeContext(), False),
        ('{"key0": {"OrbitNumberOfElectrons": 4}, "key1": {"AtomNumberOfElectrons": 2, "AtomNumberOfProtons": 5}}',
         [LeafType(Atom), LeafType(Orbit)], UnionTypeContext().dict(True), True),
    ])
    def test_one_of_custom_type(self, input_value, input_types, input_context, expected_output):
        union_type = OneOf(input_types, input_context)
        deserialized_dict_input = ApiHelper.json_deserialize(input_value, as_dict=True)
        union_type_result = union_type.validate(deserialized_dict_input)
        actual_result = union_type_result.is_valid
        deserialized_value = union_type_result.deserialize(deserialized_dict_input)
        assert actual_result == expected_output
