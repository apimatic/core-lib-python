from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core.types.union_types.union_type_context import UnionTypeContext


class AnyOf(UnionType):

    def __init__(self, union_types, union_type_context: UnionTypeContext = UnionTypeContext()):
        super(AnyOf, self).__init__(union_types, union_type_context)
        self.collection_cases = None

    def validate(self):
        return False

    def deserialize(self):
        return None

    def __deepcopy__(self, memo={}):
        copy_object = AnyOf(self._union_types, self._union_type_context)
        copy_object.is_valid = self.is_valid
        copy_object.collection_cases = self.collection_cases
        return copy_object
