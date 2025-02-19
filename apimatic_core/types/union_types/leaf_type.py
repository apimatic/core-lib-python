from datetime import date, datetime
from enum import Enum

from apimatic_core_interfaces.types.union_type import UnionType
from typing import Type, Any, Dict, List

from apimatic_core_interfaces.types.union_type_context import UnionTypeContext

from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.datetime_helper import DateTimeHelper
from apimatic_core.utilities.union_type_helper import UnionTypeHelper
from pydantic import BaseModel, validate_call


class LeafType(UnionType):

    type_to_match: Type[Any]

    @validate_call
    def __init__(self, type_to_match: Type[Any], union_type_context: UnionTypeContext = UnionTypeContext()):
        super(LeafType, self).__init__([], union_type_context)
        self.type_to_match = type_to_match

    @validate_call
    def validate(self, value: Any) -> 'UnionType':
        context = self._union_type_context

        if value is None:
            self.is_valid = context.is_nullable_or_optional
        else:
            self.is_valid = self._validate_value_against_case(value, context)

        return self

    @validate_call
    def deserialize(self, value: Any) -> Any:
        if value is None:
            return None

        context = self._union_type_context
        deserialized_value = self._deserialize_value_against_case(value, context)

        return deserialized_value

    @validate_call
    def _validate_value_against_case(self, value: Any, context: UnionTypeContext):
        if context.is_array and context.is_dict and context.is_array_of_dict:
            return self._validate_array_of_dict_case(value)

        if context.is_array and context.is_dict:
            return self._validate_dict_of_array_case(value)

        if context.is_array:
            return self._validate_array_case(value)

        if context.is_dict:
            return self._validate_dict_case(value)

        return self._validate_simple_case(value)

    @validate_call
    def _validate_dict_case(self, dict_value: Any) -> bool:
        if not isinstance(dict_value, dict):
            return False

        for key, value in dict_value.items():
            is_valid = self._validate_simple_case(value)
            if not is_valid:
                return False

        return True

    @validate_call
    def _validate_dict_of_array_case(self, dict_value: Any) -> bool:
        if not isinstance(dict_value, dict):
            return False

        for key, value in dict_value.items():
            is_valid = self._validate_array_case(value)
            if not is_valid:
                return False

        return True

    @validate_call
    def _validate_array_case(self, array_value: Any) -> bool:
        if not isinstance(array_value, list):
            return False

        for item in array_value:
            is_valid = self._validate_simple_case(item)
            if not is_valid:
                return False

        return True

    @validate_call
    def _validate_array_of_dict_case(self, array_value: Any) -> bool:
        if not isinstance(array_value, list):
            return False

        for item in array_value:
            is_valid = self._validate_dict_case(item)
            if not is_valid:
                return False

        return True

    @validate_call
    def _validate_simple_case(self, value: Any) -> bool:
        context = self._union_type_context

        if value is None or context.is_nullable_or_optional:
            return True

        if value is None or isinstance(value, list):
            return False

        return self._validate_value(value, context)

    @validate_call
    def _validate_value(self, value: Any, context: UnionTypeContext) -> bool:
        if self.type_to_match is datetime:
            return UnionTypeHelper.validate_date_time(value, context)

        if self.type_to_match is date and type(value) in [str, date]:
            return DateTimeHelper.validate_date(value)

        if issubclass(self.type_to_match, Enum) and hasattr(self.type_to_match, 'is_valid'):
            return self.type_to_match.is_valid(value)

        return self._validate_value_with_discriminator(value, context)

    @validate_call
    def _validate_value_with_discriminator(self, value: Any, context: UnionTypeContext) -> bool:
        discriminator = context.discriminator
        discriminator_value = context.discriminator_value
        if discriminator and discriminator_value:
            return self._validate_with_discriminator(discriminator, discriminator_value, value)

        if issubclass(self.type_to_match, BaseModel):
            try:
                self.type_to_match.model_validate(value)
                return True
            except:
                return False

        return type(value) is self.type_to_match

    @validate_call
    def _validate_with_discriminator(self, discriminator: str, discriminator_value: str, value: Any) -> bool:
        if not isinstance(value, dict) or value.get(discriminator) != discriminator_value:
            return False

        if issubclass(self.type_to_match, BaseModel):
            try:
                self.type_to_match.model_validate(value)
                return True
            except:
                return False

        return type(value) is self.type_to_match

    @validate_call
    def _deserialize_value_against_case(self, value: Any, context: UnionTypeContext) -> Any:
        if context.is_array and context.is_dict and context.is_array_of_dict:
            return self._deserialize_array_of_dict_case(value)

        if context.is_array and context.is_dict:
            return self._deserialize_dict_of_array_case(value)

        if context.is_array:
            return self._deserialize_array_case(value)

        if context.is_dict:
            return self._deserialize_dict_case(value)

        return self._deserialize_simple_case(value)

    @validate_call
    def _deserialize_dict_case(self, dict_value: Any) -> Dict[str, Any]:
        deserialized_value = {}
        for key, value in dict_value.items():
            result_value = self._deserialize_simple_case(value)
            deserialized_value[key] = result_value

        return deserialized_value

    @validate_call
    def _deserialize_dict_of_array_case(self, dict_value: Any) -> Dict[str, List[Any]]:
        deserialized_value = {}
        for key, value in dict_value.items():
            result_value = self._deserialize_array_case(value)
            deserialized_value[key] = result_value

        return deserialized_value

    @validate_call
    def _deserialize_array_case(self, array_value: Any) -> List[Any]:
        deserialized_value = []
        for item in array_value:
            result_value = self._deserialize_simple_case(item)
            deserialized_value.append(result_value)

        return deserialized_value

    @validate_call
    def _deserialize_array_of_dict_case(self, array_value: Any) -> List[Dict[str, Any]]:
        deserialized_value = []
        for item in array_value:
            result_value = self._deserialize_dict_case(item)
            deserialized_value.append(result_value)

        return deserialized_value

    @validate_call
    def _deserialize_simple_case(self, value: Any) -> Any:

        if issubclass(self.type_to_match, Enum):
            return self.type_to_match(value)

        if issubclass(self.type_to_match, BaseModel):
            return self.type_to_match.model_validate(value)

        if self.type_to_match is date:
            return ApiHelper.date_deserialize(value)

        if self.type_to_match is datetime:
            return ApiHelper.datetime_deserialize(
                value, self._union_type_context.date_time_format)

        return value

    @validate_call
    def __deepcopy__(self, memo={}):
        copy_object = LeafType(self.type_to_match, self._union_type_context)
        copy_object._union_types = self._union_types
        copy_object.is_valid = self.is_valid
        return copy_object
