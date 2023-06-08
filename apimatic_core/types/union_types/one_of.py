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
        is_optional_or_nullable = UnionTypeHelper.is_optional_or_nullable_case(context,
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

        return UnionTypeHelper.deserialize_value(value, self._union_type_context, self.collection_cases,
                                                 self._union_types)

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

    def _process_errors(self, value):
        self._append_nested_error_message(self._get_combined_types())

        if not self._union_type_context.is_nested:
            self._raise_validation_exception(value)

    def _get_combined_types(self):
        combined_types = []
        for union_type in self._union_types:
            if isinstance(union_type, LeafType):
                combined_types.append(union_type.type_to_match.__name__)
            elif union_type.error_messages:
                combined_types.append(', '.join(union_type.error_messages))
        return combined_types

    def _append_nested_error_message(self, combined_types):
        self.error_messages.add(', '.join(combined_types))

    def _raise_validation_exception(self, value):
        matched_count = sum(union_type.is_valid for union_type in self._union_types)
        error_message = UnionType.MORE_THAN_1_MATCHED_ERROR_MESSAGE if matched_count > 0 \
            else UnionType.NONE_MATCHED_ERROR_MESSAGE
        raise OneOfValidationException('{} \nActual Value: {}\nExpected Type: One Of {}.'.format(
            error_message, value, ', '.join(self.error_messages)))

    def __deepcopy__(self, memo={}): # pragma: no cover
        copy_object = OneOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        copy_object.error_messages = self.error_messages
        return copy_object
