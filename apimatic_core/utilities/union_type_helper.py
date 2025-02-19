import copy
from datetime import datetime

from apimatic_core_interfaces.types.union_type import UnionType
from typing import List, Any, Tuple, Dict, Set

from apimatic_core_interfaces.types.union_type_context import UnionTypeContext
from pydantic import validate_call

from apimatic_core.exceptions.anyof_validation_exception import AnyOfValidationException
from apimatic_core.exceptions.oneof_validation_exception import OneOfValidationException
from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.datetime_helper import DateTimeHelper


class UnionTypeHelper:

    NONE_MATCHED_ERROR_MESSAGE: str = 'We could not match any acceptable types against the given JSON.'
    MORE_THAN_1_MATCHED_ERROR_MESSAGE: str = 'There are more than one acceptable type matched against the given JSON.'

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def get_deserialized_value(union_types: List[UnionType], value: Any) -> Any:
        return [union_type for union_type in union_types if union_type.is_valid][0].deserialize(value)

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def validate_array_of_dict_case(
            union_types: List[UnionType], array_value: Any, is_for_one_of: bool
    ) -> Tuple[bool, List[Dict[str, List[UnionType]]]]:
        if UnionTypeHelper.is_invalid_array_value(array_value):
            return False, []

        collection_cases = []
        valid_cases = []
        for item in array_value:
            case_validity, inner_dictionary = UnionTypeHelper.validate_dict_case(union_types, item, is_for_one_of)
            collection_cases.append(inner_dictionary)
            valid_cases.append(case_validity)
        is_valid = sum(valid_cases) == array_value.__len__()
        return is_valid, collection_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def validate_dict_of_array_case(
            union_types: List[UnionType], dict_value: Any, is_for_one_of: bool
    ) -> Tuple[bool, Dict[str, List[List[UnionType]]]]:
        if UnionTypeHelper.is_invalid_dict_value(dict_value):
            return False, {}

        collection_cases = {}
        valid_cases = []
        for key, item in dict_value.items():
            case_validity, inner_array = UnionTypeHelper.validate_array_case(union_types, item, is_for_one_of)
            collection_cases[key] = inner_array
            valid_cases.append(case_validity)
        is_valid = sum(valid_cases) == dict_value.__len__()
        return is_valid, collection_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def validate_dict_case(
            union_types: List[UnionType], dict_value: Any, is_for_one_of: bool
    ) -> Tuple[bool, Dict[str, List[UnionType]]]:
        if UnionTypeHelper.is_invalid_dict_value(dict_value):
            return False, {}

        is_valid, collection_cases = UnionTypeHelper.process_dict_items(union_types, dict_value, is_for_one_of)

        return is_valid, collection_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def process_dict_items(
            union_types: List[UnionType], dict_value: Any, is_for_one_of: bool
    ) -> Tuple[bool, Dict[str, List[UnionType]]]:
        is_valid = True
        collection_cases = {}

        for key, value in dict_value.items():
            union_type_cases = UnionTypeHelper.make_deep_copies(union_types)
            matched_count = UnionTypeHelper.get_matched_count(value, union_type_cases, is_for_one_of)
            is_valid = UnionTypeHelper.check_item_validity(is_for_one_of, is_valid, matched_count)
            collection_cases[key] = union_type_cases

        return is_valid, collection_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def validate_array_case(
            union_types: List[UnionType], array_value: Any, is_for_one_of: bool
    ) -> Tuple[bool, List[List[UnionType]]]:
        if UnionTypeHelper.is_invalid_array_value(array_value):
            return False, []

        is_valid, collection_cases = UnionTypeHelper.process_array_items(union_types, array_value, is_for_one_of)

        return is_valid, collection_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def process_array_items(
            union_types: List[UnionType], array_value: Any, is_for_one_of: bool
    ) -> Tuple[bool, List[List[UnionType]]]:
        is_valid = True
        collection_cases = []

        for item in array_value:
            union_type_cases = UnionTypeHelper.make_deep_copies(union_types)
            matched_count = UnionTypeHelper.get_matched_count(item, union_type_cases, is_for_one_of)
            is_valid = UnionTypeHelper.check_item_validity(is_for_one_of, is_valid, matched_count)
            collection_cases.append(union_type_cases)

        return is_valid, collection_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def process_item(
            value: Any, union_types: List[UnionType], is_for_one_of: bool
    ) -> Tuple[bool, List[UnionType]]:
        is_valid = True
        union_type_cases = UnionTypeHelper.make_deep_copies(union_types)
        matched_count = UnionTypeHelper.get_matched_count(value, union_type_cases, is_for_one_of)
        is_valid = UnionTypeHelper.check_item_validity(is_for_one_of, is_valid, matched_count)

        return is_valid, union_type_cases

    @staticmethod
    @validate_call
    def check_item_validity(is_for_one_of: bool, is_valid: bool, matched_count: int) -> bool:
        if is_valid and is_for_one_of:
            is_valid = matched_count == 1
        elif is_valid:
            is_valid = matched_count >= 1
        return is_valid

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def make_deep_copies(union_types: List[UnionType]) -> List[UnionType]:
        nested_cases = []
        for union_type in union_types:
            nested_cases.append(copy.deepcopy(union_type))

        return nested_cases

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def get_matched_count(value: Any, union_types: List[UnionType], is_for_one_of: bool) -> int:
        matched_count = UnionTypeHelper.get_valid_cases_count(value, union_types)

        if is_for_one_of and matched_count == 1:
            return matched_count
        elif not is_for_one_of and matched_count > 0:
            return matched_count

        matched_count = UnionTypeHelper.handle_discriminator_cases(value, union_types)
        return matched_count

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def get_valid_cases_count(value: Any, union_types: List[UnionType]) -> int:
        return sum(union_type.validate(value).is_valid for union_type in union_types)

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def handle_discriminator_cases(value: Any, union_types: List[UnionType]) -> int:
        has_discriminator_cases = all(union_type.get_context().discriminator is not None and
                                      union_type.get_context().discriminator_value is not None
                                      for union_type in union_types)

        if has_discriminator_cases:
            for union_type in union_types:
                union_type.get_context().discriminator = None
                union_type.get_context().discriminator_value = None

            return UnionTypeHelper.get_valid_cases_count(value, union_types)

        return 0

    @staticmethod
    @validate_call
    def validate_date_time(value: Any, context: UnionTypeContext) -> bool:
        if isinstance(value, ApiHelper.RFC3339DateTime):
            return context.date_time_format == DateTimeFormat.RFC3339_DATE_TIME

        if isinstance(value, ApiHelper.HttpDateTime):
            return context.date_time_format == DateTimeFormat.HTTP_DATE_TIME

        if isinstance(value, ApiHelper.UnixDateTime):
            return context.date_time_format == DateTimeFormat.UNIX_DATE_TIME

        if isinstance(value, datetime) and context.date_time_converter is not None:
            serialized_dt = str(ApiHelper.when_defined(context.date_time_converter, value))
            return DateTimeHelper.validate_datetime(serialized_dt, context.date_time_format)

        return DateTimeHelper.validate_datetime(value, context.date_time_format)

    @staticmethod
    @validate_call
    def is_optional_or_nullable_case(current_context: UnionTypeContext, inner_contexts: List[UnionTypeContext]) -> bool:
        return current_context.is_nullable_or_optional or \
               any(context.is_nullable_or_optional for context in inner_contexts)

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def update_nested_flag_for_union_types(nested_union_types: List[UnionType]) -> None:
        for union_type in nested_union_types:
            union_type.get_context().is_nested = True

    @staticmethod
    @validate_call
    def is_invalid_array_value(value: Any) -> bool:
        return value is None or not isinstance(value, list)

    @staticmethod
    @validate_call
    def is_invalid_dict_value(value: Any) -> bool:
        return value is None or not isinstance(value, dict)

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def deserialize_value(
            value: Any, context: UnionTypeContext, collection_cases: Any, union_types: List[UnionType]
    ) -> Any:
        if context.is_array and context.is_dict and context.is_array_of_dict:
            return UnionTypeHelper.deserialize_array_of_dict_case(value, collection_cases)

        if context.is_array and context.is_dict:
            return UnionTypeHelper.deserialize_dict_of_array_case(value, collection_cases)

        if context.is_array:
            return UnionTypeHelper.deserialize_array_case(value, collection_cases)

        if context.is_dict:
            return UnionTypeHelper.deserialize_dict_case(value, collection_cases)

        return UnionTypeHelper.get_deserialized_value(union_types, value)

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def deserialize_array_of_dict_case(
            array_value: List[Dict[str, Any]], collection_cases: List[Dict[str, List[UnionType]]]
    ) -> List[Dict[str, Any]]:
        deserialized_value = []
        for index, item in enumerate(array_value):
            deserialized_value.append(UnionTypeHelper.deserialize_dict_case(item, collection_cases[index]))

        return deserialized_value

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def deserialize_dict_of_array_case(
            dict_value: Dict[str, List[Any]], collection_cases: Dict[str, List[List[UnionType]]]
    ) -> Dict[str, List[Any]]:
        deserialized_value = {}
        for key, value in dict_value.items():
            deserialized_value[key] = UnionTypeHelper.deserialize_array_case(value, collection_cases[key])

        return deserialized_value

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def deserialize_dict_case(
            dict_value: Dict[str, Any], collection_cases: Dict[str, List[UnionType]]
    ) -> Dict[str, Any]:
        deserialized_value = {}
        for key, value in dict_value.items():
            valid_case = [case for case in collection_cases[key] if case.is_valid][0]
            deserialized_value[key] = valid_case.deserialize(value)

        return deserialized_value

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def deserialize_array_case(array_value: List[Any], collection_cases: List[List[UnionType]]) -> List[Any]:
        deserialized_value = []
        for index, item in enumerate(array_value):
            valid_case = [case for case in collection_cases[index] if case.is_valid][0]
            deserialized_value.append(valid_case.deserialize(item))

        return deserialized_value

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def process_errors(
            value: Any, union_types: List[UnionType], error_messages: Set[str], is_nested: bool, is_for_one_of: bool
    ) -> Set[str]:
        error_messages.add(', '.join(UnionTypeHelper.get_combined_error_messages(union_types)))

        if not is_nested:
            UnionTypeHelper.raise_validation_exception(value, union_types, ', '.join(error_messages), is_for_one_of)

        return error_messages

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def get_combined_error_messages(union_types: List[UnionType]) -> List[str]:
        combined_error_messages = []
        from apimatic_core.types.union_types.leaf_type import LeafType
        for union_type in union_types:
            if isinstance(union_type, LeafType):
                combined_error_messages.append(union_type.type_to_match.__name__)
            elif union_type.error_messages:
                combined_error_messages.append(', '.join(union_type.error_messages))
        return combined_error_messages

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def raise_validation_exception(value: Any, union_types: List[UnionType], error_message: str, is_for_one_of: bool):
        if is_for_one_of:
            matched_count = sum(union_type.is_valid for union_type in union_types)
            message = UnionTypeHelper.MORE_THAN_1_MATCHED_ERROR_MESSAGE if matched_count > 0 \
                else UnionTypeHelper.NONE_MATCHED_ERROR_MESSAGE
            raise OneOfValidationException('{} \nActual Value: {}\nExpected Type: One Of {}.'.format(
                message, value, error_message))
        else:
            raise AnyOfValidationException('{} \nActual Value: {}\nExpected Type: Any Of {}.'.format(
                UnionTypeHelper.NONE_MATCHED_ERROR_MESSAGE, value, error_message))
