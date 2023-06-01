import copy
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

        for union_type in self._union_types:
            union_type.get_context().is_nested = True

        is_optional_or_nullable = context.is_nullable_or_optional() or any(
            union_type.get_context().is_nullable_or_optional() for union_type in self._union_types)

        if value is None and is_optional_or_nullable:
            self.is_valid = True
            return self

        if value is None:
            self.is_valid = False
            self.process_errors(value)
            return self

        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            if isinstance(value, list):
                self.is_valid, self.collection_cases = UnionTypeHelper.validate_array_of_dict_case(self._union_types,
                                                                                                   value, True)
            else:
                self.is_valid = False
        elif context.is_array() and context.is_dict():
            if isinstance(value, dict):
                self.is_valid, self.collection_cases = UnionTypeHelper.validate_dict_of_array_case(self._union_types,
                                                                                                   value, True)
            else:
                self.is_valid = False
        elif context.is_array():
            if isinstance(value, list):
                self.is_valid, self.collection_cases = UnionTypeHelper.validate_array_case(self._union_types,
                                                                                           value, True)
            else:
                self.is_valid = False
        elif context.is_dict():
            if isinstance(value, dict):
                self.is_valid, self.collection_cases = UnionTypeHelper.validate_dict_case(self._union_types,
                                                                                          value, True)
            else:
                self.is_valid = False
        else:
            self.is_valid = UnionTypeHelper.get_matched_count(value, self._union_types, True) == 1

        if not self.is_valid:
            self.process_errors(value)

        return self

    def process_errors(self, value):
        self.error_messages = []

        combined_types = []
        for union_type in self._union_types:
            if isinstance(union_type, LeafType):
                combined_types.append(union_type.type_to_match.__name__)
            else:
                combined_types.append(', '.join(union_type.error_messages))

        if self._union_type_context.is_nested:
            self.error_messages.append(', '.join(combined_types))
        else:
            matched_count = sum(union_type.is_valid for union_type in self._union_types)
            error_message = UnionType.MORE_THAN_1_MATCHED_ERROR_MESSAGE if matched_count > 0 \
                else UnionType.NONE_MATCHED_ERROR_MESSAGE
            raise OneOfValidationException('{} \nActual Value: {}\nExpected Type: One Of {}.'.format(
                error_message, value, ', '.join(combined_types)))

    def deserialize(self, value):
        if value is None or not self.is_valid:
            return None

        context = self._union_type_context

        if value is None and context.is_nullable_or_optional():
            return None

        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            deserialized_value = UnionTypeHelper.deserialize_array_of_dict_case(value, self.collection_cases)
        elif context.is_array() and context.is_dict():
            deserialized_value = UnionTypeHelper.deserialize_dict_of_array_case(value, self.collection_cases)
        elif context.is_array():
            deserialized_value = UnionTypeHelper.deserialize_array_case(value, self.collection_cases)
        elif context.is_dict():
            deserialized_value = UnionTypeHelper.deserialize_dict_case(value, self.collection_cases)
        else:
            deserialized_value = UnionTypeHelper.get_deserialized_value(self._union_types, value)

        return deserialized_value

    def __deepcopy__(self, memo={}):
        copy_object = OneOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        return copy_object
