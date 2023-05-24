import pytest
from apimatic_core.types.union_types.any_of import AnyOf
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.union_type_context import UnionTypeContext


class TestAnyOf:

    @pytest.mark.parametrize('input_value, input_types, input_outer_context, expected_validity', [
        (100, [LeafType(int), LeafType(str)], UnionTypeContext(), True)
    ])
    def test_any_of_primitive_type_validity(self, input_value, input_types, input_outer_context, expected_validity):
        union_type = AnyOf(input_types, input_outer_context)
        actual_result = union_type.validate(input_value)
        assert actual_result.is_valid == expected_validity
