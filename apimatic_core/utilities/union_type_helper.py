
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

    @staticmethod
    def get_matched_count(value, union_types, is_for_one_of):
        matched_count = sum(union_type.validate(value).is_valid for union_type in union_types)

        if is_for_one_of and matched_count == 1:
            return matched_count
        elif not is_for_one_of and matched_count > 0:
            return matched_count

        # Check through normal schema validation flow when discriminator exits but still invalid
        has_discriminator_cases = all(union_type.get_context().get_discriminator() is not None and
                                      union_type.get_context().get_discriminator_value() is not None
                                      for union_type in union_types)
        if matched_count == 0 and has_discriminator_cases:
            for union_type in union_types:
                union_type.get_context().discriminator(None)
                union_type.get_context().discriminator_value(None)
            matched_count = sum(union_type.validate(value).is_valid for union_type in union_types)

        return matched_count
