import copy


class UnionTypeHelper:

    @staticmethod
    def get_deserialized_value(union_types, value):
        return [union_type for union_type in union_types if union_type.is_valid][0].deserialize(value)

    @staticmethod
    def validate_array_of_dict_case(union_types, array_value, is_for_one_of):
        if array_value is None or not array_value:
            return tuple((False, []))

        collection_cases = []
        valid_cases = []
        for item in array_value:
            case_validity, inner_dictionary = UnionTypeHelper.validate_dict_case(union_types, item, is_for_one_of)
            collection_cases.append(inner_dictionary)
            valid_cases.append(case_validity)
        is_valid = sum(valid_cases) == array_value.__len__()
        return tuple((is_valid, collection_cases))

    @staticmethod
    def validate_dict_of_array_case(union_types, dict_value, is_for_one_of):
        if dict_value is None or not dict_value:
            return tuple((False, []))

        collection_cases = {}
        valid_cases = []
        for key, item in dict_value.items():
            case_validity, inner_array = UnionTypeHelper.validate_array_case(union_types, item, is_for_one_of)
            collection_cases[key] = inner_array
            valid_cases.append(case_validity)
        is_valid = sum(valid_cases) == dict_value.__len__()
        return tuple((is_valid, collection_cases))

    @staticmethod
    def validate_dict_case(union_types, dict_value, is_for_one_of):
        if dict_value is None or not dict_value:
            return tuple((False, []))

        is_valid = True
        collection_cases = {}
        for key, value in dict_value.items():
            nested_cases = []
            for union_type in union_types:
                nested_cases.append(copy.deepcopy(union_type).validate(value))
            matched_count = UnionTypeHelper.get_matched_count(value, nested_cases, True)
            if is_valid:
                is_valid = matched_count == 1 if is_for_one_of else matched_count >= 1
            collection_cases[key] = nested_cases
        return tuple((is_valid, collection_cases))

    @staticmethod
    def validate_array_case(union_types, array_value, is_for_one_of):
        if array_value is None or not array_value:
            return tuple((False, []))

        is_valid = True
        collection_cases = []
        for item in array_value:
            nested_cases = []
            for union_type in union_types:
                nested_cases.append(copy.deepcopy(union_type).validate(item))
            matched_count = UnionTypeHelper.get_matched_count(item, nested_cases, True)
            if is_valid:
                is_valid = matched_count == 1 if is_for_one_of else matched_count >= 1
            collection_cases.append(nested_cases)
        return tuple((is_valid, collection_cases))

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
