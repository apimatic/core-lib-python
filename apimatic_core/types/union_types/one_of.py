from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core_interfaces.types.union_type_context import UnionTypeContext
from typing import List, Any

from pydantic import validate_call

from apimatic_core.utilities.union_type_helper import UnionTypeHelper


class OneOf(UnionType):

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, union_types: List[UnionType], union_type_context: UnionTypeContext = UnionTypeContext()):
        super(OneOf, self).__init__(union_types, union_type_context)
        self.collection_cases: Any = None

    @validate_call
    def validate(self, value: Any) -> 'UnionType':
        context = self._union_type_context
        UnionTypeHelper.update_nested_flag_for_union_types(self._union_types)
        is_optional_or_nullable = UnionTypeHelper.is_optional_or_nullable_case(
            context, [nested_type.get_context() for nested_type in self._union_types])

        if value is None and is_optional_or_nullable:
            self.is_valid = True
            return self

        if value is None:
            self.is_valid = False
            self.error_messages = UnionTypeHelper.process_errors(
                value, self._union_types, self.error_messages, self.get_context().is_nested, True)
            return self

        self._validate_value_against_case(value, context)

        if not self.is_valid:
            self.error_messages = UnionTypeHelper.process_errors(
                value, self._union_types, self.error_messages, self.get_context().is_nested, True)

        return self

    @validate_call
    def deserialize(self, value: Any) -> Any:
        if value is None:
            return None

        return UnionTypeHelper.deserialize_value(
            value, self._union_type_context, self.collection_cases, self._union_types
        )

    @validate_call
    def _validate_value_against_case(self, value: Any, context: UnionTypeContext):
        if context.is_array and context.is_dict and context.is_array_of_dict:
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_array_of_dict_case(
                self._union_types, value, True)
        elif context.is_array and context.is_dict:
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_dict_of_array_case(
                self._union_types, value, True)
        elif context.is_array:
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_array_case(
                self._union_types, value, True)
        elif context.is_dict:
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_dict_case(
                self._union_types, value, True)
        else:
            self.is_valid = UnionTypeHelper.get_matched_count(value, self._union_types, True) == 1

    @validate_call
    def __deepcopy__(self, memo={}):
        copy_object = OneOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        copy_object.error_messages = self.error_messages
        return copy_object
