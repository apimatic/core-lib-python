import copy
from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.union_type_helper import UnionTypeHelper


class OneOf(UnionType):

    def __init__(self, union_types, union_type_context: UnionTypeContext = UnionTypeContext()):
        super(OneOf, self).__init__(union_types, union_type_context)
        self.collection_cases = None

    def validate(self, value):
        context = self._union_type_context

        if value is None and context.is_nullable_or_optional():
            self.is_valid = True
            return self

        if value is None:
            self.is_valid = False
            return self

        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            if isinstance(value, list):
                self.is_valid, self.collection_cases = self.validate_array_of_dict_case(value)
            else:
                self.is_valid = False
        elif context.is_array() and context.is_dict():
            if isinstance(value, dict):
                self.is_valid, self.collection_cases = self.validate_dict_of_array_case(value)
            else:
                self.is_valid = False
        elif context.is_array():
            if isinstance(value, list):
                self.is_valid, self.collection_cases = self.validate_array_case(value)
            else:
                self.is_valid = False
        elif context.is_dict():
            if isinstance(value, dict):
                self.is_valid, self.collection_cases = self.validate_dict_case(value)
            else:
                self.is_valid = False
        else:
            self.is_valid = ApiHelper.get_matched_count(value, self._union_types, True) == 1

        return self

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
            deserialized_value = self.get_deserialized_value(value)

        return deserialized_value

    def get_deserialized_value(self, value):
        return [union_type for union_type in self._union_types if union_type.is_valid][0].deserialize(value)

    def validate_array_of_dict_case(self, array_value):
        if array_value is None or not array_value:
            return tuple((False, []))

        collection_cases = []
        valid_cases = []
        for item in array_value:
            case_validity, inner_dictionary = self.validate_dict_case(item)
            collection_cases.append(inner_dictionary)
            valid_cases.append(case_validity)
        is_valid = sum(valid_cases) == array_value.__len__()

        return tuple((is_valid, collection_cases))

    def validate_dict_of_array_case(self, dict_value):
        if dict_value is None or not dict_value:
            return tuple((False, []))

        collection_cases = {}
        valid_cases = []
        for key, item in dict_value.items():
            case_validity, inner_array = self.validate_array_case(item)
            collection_cases[key] = inner_array
            valid_cases.append(case_validity)
        is_valid = sum(valid_cases) == dict_value.__len__()

        return tuple((is_valid, collection_cases))

    def validate_dict_case(self, dict_value):
        if dict_value is None or not dict_value:
            return tuple((False, []))

        is_valid = True
        collection_cases = {}
        for key, value in dict_value.items():
            nested_cases = []
            for union_type in self._union_types:
                nested_cases.append(copy.deepcopy(union_type).validate(value))
            matched_count = ApiHelper.get_matched_count(value, nested_cases, True)
            if is_valid:
                is_valid = matched_count == 1
            collection_cases[key] = nested_cases

        return tuple((is_valid, collection_cases))

    def validate_array_case(self, array_value):
        if array_value is None or not array_value:
            return tuple((False, []))

        is_valid = True
        collection_cases = []
        for item in array_value:
            nested_cases = []
            for union_type in self._union_types:
                nested_cases.append(copy.deepcopy(union_type).validate(item))
            matched_count = ApiHelper.get_matched_count(item, nested_cases, True)
            if is_valid:
                is_valid = matched_count == 1
            collection_cases.append(nested_cases)

        return tuple((is_valid, collection_cases))

    def __deepcopy__(self, memo={}):
        copy_object = OneOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        return copy_object
