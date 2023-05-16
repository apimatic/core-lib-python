import pytest
from apimatic_core.types.union_types.any_of import AnyOf


class TestAnyOf:

    @pytest.mark.parametrize('input_value, types, expected_output', [
        (100, {int, str}, True)
    ])
    def test_any_of_primitive_type(self, input_value, types, expected_output):
        union_type = AnyOf()
        actual_result = union_type.validate()
        assert actual_result == expected_output
