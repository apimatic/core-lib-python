from datetime import date, datetime

import dateutil
from apimatic_core_interfaces.types.union_type import UnionType

from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.datetime_helper import DateTimeHelper


class LeafType(UnionType):

    def __init__(self, type_to_match: type, union_type_context: UnionTypeContext = UnionTypeContext()):
        super(LeafType, self).__init__(None, union_type_context)
        self.type_to_match = type_to_match

    def validate(self, value):
        context = self._union_type_context

        if value is None and context.is_nullable_or_nullable():
            self.is_valid = True
            return self.is_valid

        if value is None:
            self.is_valid = False
            return self.is_valid

        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            self.is_valid = self.validate_array_of_dict_case(value)
        elif context.is_array() and context.is_dict():
            self.is_valid = self.validate_dict_of_array_case(value)
        elif context.is_array():
            self.is_valid = self.validate_array_case(value)
        elif context.is_dict():
            self.is_valid = self.validate_dict_case(value)
        else:
            self.is_valid = self.validate_item(value)

        return self

    def deserialize(self, value):
        if value is None or not self.is_valid:
            return None

        context = self._union_type_context
        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            deserialized_value = self.deserialize_array_of_dict_case(value)
        elif context.is_array() and context.is_dict():
            deserialized_value = self.deserialize_dict_of_array_case(value)
        elif context.is_array():
            deserialized_value = self.deserialize_array_case(value)
        elif context.is_dict():
            deserialized_value = self.deserialize_dict_case(value)
        else:
            deserialized_value = self.deserialize_item(value)

        return deserialized_value

    def validate_dict_case(self, dict_value):
        if not isinstance(dict_value, dict):
            return False

        for key, value in dict_value.items():
            is_valid = self.validate_item(value)
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
            is_valid = self.validate_item(item)
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

    def validate_item(self, value):
        context = self._union_type_context

        if value is None or context.is_nullable_or_optional():
            return True

        if value is None or isinstance(value, list):
            return False

        if self.type_to_match in [datetime]:
            if isinstance(value, ApiHelper.RFC3339DateTime):
                return context.get_date_time_format() == DateTimeFormat.RFC3339_DATE_TIME
            elif isinstance(value, ApiHelper.HttpDateTime):
                return context.get_date_time_format() == DateTimeFormat.HTTP_DATE_TIME
            elif isinstance(value, ApiHelper.UnixDateTime):
                return context.get_date_time_format() == DateTimeFormat.UNIX_DATE_TIME
            else:
                return DateTimeHelper.validate_datetime(value, self._union_type_context.get_date_time_format())

        if self.type_to_match is date:
            return DateTimeHelper.validate_date(value)

        is_native_type = self.type_to_match in UnionType.NATIVE_TYPES

        if is_native_type:
            return isinstance(value, self.type_to_match)

        discriminator = self._union_type_context.get_discriminator()
        discriminator_value = self._union_type_context.get_discriminator_value()
        if discriminator and discriminator_value:
            return value.get(discriminator) == discriminator_value and self.type_to_match.validate(value)

        if hasattr(self.type_to_match, 'validate'):
            return self.type_to_match.validate(value)

        return False

    def deserialize_dict_case(self, dict_value):
        if not isinstance(dict_value, dict):
            return None

        deserialized_value = {}
        for key, value in dict_value.items():
            result_value = self.deserialize_item(value)
            deserialized_value[key] = result_value

        return deserialized_value

    def deserialize_dict_of_array_case(self, dict_value):
        if not isinstance(dict_value, dict):
            return None

        deserialized_value = {}
        for key, value in dict_value.items():
            result_value = self.deserialize_array_case(value)
            deserialized_value[key] = result_value

        return deserialized_value

    def deserialize_array_case(self, array_value):
        if not isinstance(array_value, list):
            return None

        deserialized_value = []
        for item in array_value:
            result_value = self.deserialize_item(item)
            deserialized_value.append(result_value)

        return deserialized_value

    def deserialize_array_of_dict_case(self, array_value):
        if not isinstance(array_value, list):
            return None

        deserialized_value = []
        for item in array_value:
            result_value = self.deserialize_dict_case(item)
            deserialized_value.append(result_value)

        return deserialized_value

    def deserialize_item(self, value):
        is_native_type = self.type_to_match in UnionType.NATIVE_TYPES

        if self.type_to_match is date:
            return ApiHelper.date_deserialize(value)
        elif self.type_to_match is datetime:
            return ApiHelper.datetime_deserialize(
                value, self._union_type_context.get_date_time_format())
        elif is_native_type:
            return value
        elif hasattr(self.type_to_match, 'from_dictionary'):
            return self.type_to_match.from_dictionary(value)

        return None

    def __deepcopy__(self, memo={}):
        copy_object = LeafType(self.type_to_match, self._union_type_context)
        copy_object._union_types = self._union_types
        copy_object.is_valid = self.is_valid
        return copy_object
