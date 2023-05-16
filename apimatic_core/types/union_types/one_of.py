import copy
from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core.types.union_types.union_type_context import UnionTypeContext


class OneOf(UnionType):

    def __init__(self, union_types, union_type_context: UnionTypeContext = UnionTypeContext()):
        super(OneOf, self).__init__(union_types, union_type_context)
        self.collection_cases = None

    def validate(self, value):
        context = self._union_type_context

        if value is None and context.is_nullable_or_nullable():
            self.is_valid = True
            return self

        if value is None:
            self.is_valid = False
            return self

        if context.is_array() and context.is_dict() and context.is_array_of_dict():
            if isinstance(value, list):
                self.is_valid = self.validate_array_of_dict_case(value)
            else:
                self.is_valid = False
        elif context.is_array() and context.is_dict():
            if isinstance(value, dict):
                self.is_valid = self.validate_dict_of_array_case(value)
            else:
                self.is_valid = False
        elif context.is_array():
            if isinstance(value, list):
                self.is_valid = self.validate_array_case(value)
            else:
                self.is_valid = False
        elif context.is_dict():
            if isinstance(value, dict):
                self.is_valid = self.validate_dict_case(value)
            else:
                self.is_valid = False
        else:
            matched_count = sum(union_type.validate(value).is_valid for union_type in self._union_types)
            self.is_valid = matched_count == 1

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
            deserialized_value = self.get_deserialized_value(value)

        return deserialized_value

    def get_deserialized_value(self, value):
        return [union_type.deserialize(value) for union_type in self._union_types if union_type.is_valid][0]

    def validate_array_of_dict_case(self, array_value):
        if array_value is None or not array_value:
            return False

        matched_count = sum(self.validate_dict_case(item) for item in array_value)
        return matched_count == array_value.__len__()

    def validate_dict_of_array_case(self, dict_value):
        if dict_value is None or not dict_value:
            return False

        matched_count = sum(self.validate_array_case(item) for item in dict_value.values())
        return matched_count == dict_value.__len__()

    def validate_dict_case(self, dict_value):
        if dict_value is None or not dict_value:
            return False

        is_valid = True
        self.collection_cases = {}
        for key, value in dict_value.items():
            nested_cases = []
            for union_type in self._union_types:
                nested_cases.append(copy.deepcopy(union_type).validate(value))
            matched_count = sum(processed_inner_type.is_valid for processed_inner_type in nested_cases)
            if is_valid:
                is_valid = matched_count == 1
            self.collection_cases[key] = nested_cases
        return is_valid

    def validate_array_case(self, array_value):
        if array_value is None or not array_value:
            return False

        is_valid = True
        self.collection_cases = []
        for item in array_value:
            nested_cases = []
            for union_type in self._union_types:
                nested_cases.append(copy.deepcopy(union_type).validate(item))
            matched_count = sum(processed_inner_type.is_valid for processed_inner_type in nested_cases)
            if is_valid:
                is_valid = matched_count == 1
            self.collection_cases.append(nested_cases)
        return is_valid

    def deserialize_array_of_dict_case(self, array_value):
        if array_value is None:
            return False

        return [self.deserialize_dict_case(item) for item in array_value]

    def deserialize_dict_of_array_case(self, dict_value):
        if dict_value is None:
            return False

        deserialized_value = {}
        for key, value in dict_value.items():
            deserialized_value[key] = self.deserialize_array_case(value)

        return deserialized_value

    def deserialize_dict_case(self, dict_value):
        if dict_value is None:
            return False

        deserialized_value = {}
        for key, value in dict_value.items():
            valid_case = [case for case in self.collection_cases[key] if case.is_valid][0]
            deserialized_value[key] = valid_case.deserialize(value)

        return deserialized_value

    def deserialize_array_case(self, array_value):
        if array_value is None:
            return False

        deserialized_value = []
        for index, item in enumerate(array_value):
            valid_case = [case for case in self.collection_cases[index] if case.is_valid][0]
            deserialized_value.append(valid_case.deserialize(item))

        return deserialized_value

    def __deepcopy__(self, memo={}):
        copy_object = OneOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        return copy_object
