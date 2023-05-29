
class UnionTypeHelper:
    @staticmethod
    def deserialize_array_of_dict_case(array_value, collection_cases):
        if array_value is None:
            return None
        deserialized_value = []
        for index, item in enumerate(array_value):
            deserialized_value.append(UnionTypeHelper.deserialize_dict_case(item, collection_cases[index]))

        return deserialized_value

    @staticmethod
    def deserialize_dict_of_array_case(dict_value, collection_cases):
        if dict_value is None:
            return None

        deserialized_value = {}
        for key, value in dict_value.items():
            deserialized_value[key] = UnionTypeHelper.deserialize_array_case(value, collection_cases[key])

        return deserialized_value

    @staticmethod
    def deserialize_dict_case(dict_value, collection_cases):
        if dict_value is None:
            return None

        deserialized_value = {}
        for key, value in dict_value.items():
            valid_case = [case for case in collection_cases[key] if case.is_valid][0]
            deserialized_value[key] = valid_case.deserialize(value)

        return deserialized_value

    @staticmethod
    def deserialize_array_case(array_value, collection_cases):
        if array_value is None:
            return None

        deserialized_value = []
        for index, item in enumerate(array_value):
            valid_case = [case for case in collection_cases[index] if case.is_valid][0]
            deserialized_value.append(valid_case.deserialize(item))

        return deserialized_value
