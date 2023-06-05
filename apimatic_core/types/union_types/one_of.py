from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core.exceptions.oneof_validation_exception import OneOfValidationException
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.union_type_helper import UnionTypeHelper


class OneOf(UnionType):

    def __init__(self, union_types, union_type_context: UnionTypeContext = UnionTypeContext()):
        super(OneOf, self).__init__(union_types, union_type_context)
        self.collection_cases = None

    def validate(self, value):
        context = self._union_type_context
        UnionTypeHelper.update_nested_flag_for_union_types(self._union_types)
        is_optional_or_nullable = UnionTypeHelper.is_optional_or_nullable_case(self._union_type_context,
                                                                               [nested_type.get_context()
                                                                                for nested_type in self._union_types])

        if value is None and is_optional_or_nullable:
            self.is_valid = True
            return self

        if value is None:
            self.is_valid = False
            self._process_errors(value)
            return self

        self._validate_value_against_case(value, context)

        if not self.is_valid:
            self._process_errors(value)

        return self

    def deserialize(self, value):
        if value is None:
            return None

        context = self._union_type_context
        deserialized_value = self._deserialize_value_against_case(value, context)
        return deserialized_value

    def _validate_value_against_case(self, value, context):
        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_array_of_dict_case(self._union_types, value,
                                                                                               True)
        elif context.is_array() and context.is_dict():
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_dict_of_array_case(self._union_types, value,
                                                                                               True)
        elif context.is_array():
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_array_case(self._union_types, value, True)
        elif context.is_dict():
            self.is_valid, self.collection_cases = UnionTypeHelper.validate_dict_case(self._union_types, value, True)
        else:
            self.is_valid = UnionTypeHelper.get_matched_count(value, self._union_types, True) == 1

    def _deserialize_value_against_case(self, value, context):
        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            return UnionTypeHelper.deserialize_array_of_dict_case(value, self.collection_cases)

        if context.is_array() and context.is_dict():
            return UnionTypeHelper.deserialize_dict_of_array_case(value, self.collection_cases)

        if context.is_array():
            return UnionTypeHelper.deserialize_array_case(value, self.collection_cases)

        if context.is_dict():
            return UnionTypeHelper.deserialize_dict_case(value, self.collection_cases)

        return UnionTypeHelper.get_deserialized_value(self._union_types, value)

    def _process_errors(self, value):
        self.error_messages = []

        combined_types = self._get_combined_types()

        if self._union_type_context.is_nested:
            self._append_nested_error_message(combined_types)
        else:
            self._raise_validation_exception(value, combined_types)

    def _get_combined_types(self):
        combined_types = []
        for union_type in self._union_types:
            if isinstance(union_type, LeafType):
                combined_types.append(union_type.type_to_match.__name__)
            else:
                combined_types.append(', '.join(union_type.error_messages))
        return combined_types

    def _append_nested_error_message(self, combined_types):
        self.error_messages.append(', '.join(combined_types))

    def _raise_validation_exception(self, value, combined_types):
        matched_count = sum(union_type.is_valid for union_type in self._union_types)
        error_message = UnionType.MORE_THAN_1_MATCHED_ERROR_MESSAGE if matched_count > 0 \
            else UnionType.NONE_MATCHED_ERROR_MESSAGE
        raise OneOfValidationException('{} \nActual Value: {}\nExpected Type: One Of {}.'.format(
            error_message, value, ', '.join(combined_types)))

    def __deepcopy__(self, memo={}):
        copy_object = OneOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        return copy_object
