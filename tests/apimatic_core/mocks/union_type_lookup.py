
from apimatic_core_interfaces.types.union_type import UnionType
from apimatic_core_interfaces.types.union_type_context import UnionTypeContext as Context
from typing import Dict

from pydantic import validate_call

from apimatic_core.types.union_types.any_of import AnyOf
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.one_of import OneOf


class UnionTypeLookUp:

    """
    The `UnionTypeLookUp` class serves as a utility class for storing and managing type combinator templates.
    It acts as a container for the templates used in handling various data types within the application.
    """
    _union_types: Dict[str, UnionType] = {
        'ScalarModelAnyOfRequired': AnyOf(
            [LeafType(float), LeafType(bool)]
        ),
        'ScalarModelOneOfReqNullable': OneOf(
            [LeafType(int), LeafType(str)], Context.create(is_nullable=True)
        ),
        'ScalarModelOneOfOptional': OneOf(
            [LeafType(int), LeafType(float), LeafType(str)], Context.create(is_optional=True)
        ),
        'ScalarModelAnyOfOptNullable': AnyOf(
            [LeafType(int), LeafType(bool)], Context.create(is_optional=True, is_nullable=True)
        ),
        'ScalarTypes': OneOf([LeafType(float), LeafType(bool)]),
    }

    @staticmethod
    @validate_call
    def get(name: str) -> UnionType:
        return UnionTypeLookUp._union_types[name]

