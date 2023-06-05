from datetime import date, datetime
from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.datetime_helper import DateTimeHelper
from apimatic_core.utilities.union_type_helper import UnionTypeHelper


class LeafType(UnionType):

    def __init__(self, type_to_match: type, union_type_context: UnionTypeContext = UnionTypeContext()):
        super(LeafType, self).__init__(None, union_type_context)
        self.type_to_match = type_to_match

    def validate(self, value):
        context = self._union_type_context

        if value is None:
            self.is_valid = context.is_nullable_or_optional()
        else:
            self.is_valid = self.validate_value_against_case(value, context)

        return self

    def deserialize(self, value):
        if value is None:
            return None

        context = self._union_type_context
        deserialized_value = self.deserialize_value_against_case(value, context)

        return deserialized_value

    def validate_value_against_case(self, value, context):
        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            return self.validate_array_of_dict_case(value)

        if context.is_array() and context.is_dict():
            return self.validate_dict_of_array_case(value)

        if context.is_array():
            return self.validate_array_case(value)

        if context.is_dict():
            return self.validate_dict_case(value)

        return self.validate_simple_case(value)

    def validate_dict_case(self, dict_value):
        if not isinstance(dict_value, dict):
            return False

        for key, value in dict_value.items():
            is_valid = self.validate_simple_case(value)
            if not is_valid:
                return False

        return True

    def validate_dict_of_array_case(self, dict_value):
        if not isinstance(dict_value, dict):
            return False

        for key, value in dict_value.items():
            is_valid = self.validate_array_case(value)
            if not is_valid:
                return False

        return True

    def validate_array_case(self, array_value):
        if not isinstance(array_value, list):
            return False

        for item in array_value:
            is_valid = self.validate_simple_case(item)
            if not is_valid:
                return False

        return True

    def validate_array_of_dict_case(self, array_value):
        if not isinstance(array_value, list):
            return False

        for item in array_value:
            is_valid = self.validate_dict_case(item)
            if not is_valid:
                return False

        return True

    def validate_simple_case(self, value):
        context = self._union_type_context

        if value is None or context.is_nullable_or_optional():
            return True

        if value is None or isinstance(value, list):
            return False

        return self.validate_value(value, context)

    def validate_value(self, value, context):
        if self.type_to_match is datetime:
            return UnionTypeHelper.validate_date_time(value, context)

        if self.type_to_match is date:
            return DateTimeHelper.validate_date(value)

        return self.validate_value_with_discriminator(value, context)

    def validate_value_with_discriminator(self, value, context):
        discriminator = context.get_discriminator()
        discriminator_value = context.get_discriminator_value()
        if discriminator and discriminator_value:
            return self.validate_with_discriminator(discriminator, discriminator_value, value)

        if hasattr(self.type_to_match, 'validate'):
            return self.type_to_match.validate(value)

        return type(value) is self.type_to_match

    def validate_with_discriminator(self, discriminator, discriminator_value, value):
        if not isinstance(value, dict) or value.get(discriminator) != discriminator_value:
            return False

        if hasattr(self.type_to_match, 'validate'):
            return self.type_to_match.validate(value)

        return type(value) is self.type_to_match

    def deserialize_value_against_case(self, value, context):
        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            return self.deserialize_array_of_dict_case(value)

        if context.is_array() and context.is_dict():
            return self.deserialize_dict_of_array_case(value)

        if context.is_array():
            return self.deserialize_array_case(value)

        if context.is_dict():
            return self.deserialize_dict_case(value)

        return self.deserialize_simple_case(value)

    def deserialize_dict_case(self, dict_value):
        deserialized_value = {}
        for key, value in dict_value.items():
            result_value = self.deserialize_simple_case(value)
            deserialized_value[key] = result_value

        return deserialized_value

    def deserialize_dict_of_array_case(self, dict_value):
        deserialized_value = {}
        for key, value in dict_value.items():
            result_value = self.deserialize_array_case(value)
            deserialized_value[key] = result_value

        return deserialized_value

    def deserialize_array_case(self, array_value):
        deserialized_value = []
        for item in array_value:
            result_value = self.deserialize_simple_case(item)
            deserialized_value.append(result_value)

        return deserialized_value

    def deserialize_array_of_dict_case(self, array_value):
        deserialized_value = []
        for item in array_value:
            result_value = self.deserialize_dict_case(item)
            deserialized_value.append(result_value)

        return deserialized_value

    def deserialize_simple_case(self, value):
        if hasattr(self.type_to_match, 'from_dictionary'):
            return self.type_to_match.from_dictionary(value)

        if self.type_to_match is date:
            return ApiHelper.date_deserialize(value)

        if self.type_to_match is datetime:
            return ApiHelper.datetime_deserialize(
                value, self._union_type_context.get_date_time_format())

        return value

    def __deepcopy__(self, memo={}):
        copy_object = LeafType(self.type_to_match, self._union_type_context)
        copy_object._union_types = self._union_types
        copy_object.is_valid = self.is_valid
        return copy_object
