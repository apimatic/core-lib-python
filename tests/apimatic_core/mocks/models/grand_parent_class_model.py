from typing import Optional, List

from pydantic import BaseModel, AliasChoices, Field, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper


class GrandParentClassModel(BaseModel):

    """Implementation of the 'Grand Parent Class' model.

    TODO: type model description here.

    Attributes:
        grand_parent_optional (str): TODO: type description here.
        grand_parent_required_nullable (str): TODO: type description here.
        grand_parent_required (str): TODO: type description here.

    """

    grand_parent_required_nullable: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("grand_parent_required_nullable", "Grand_Parent_Required_Nullable"),
              serialization_alias="Grand_Parent_Required_Nullable")
    ]
    grand_parent_required: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("grand_parent_required", "Grand_Parent_Required"),
              serialization_alias="Grand_Parent_Required")
    ] = 'not nullable and required'
    grand_parent_optional: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("grand_parent_optional", "Grand_Parent_Optional"),
              serialization_alias="Grand_Parent_Optional")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _nullable_fields = {'grand_parent_required_nullable'}
        _optional_fields = {'grand_parent_optional'}

        return ApiHelper.sanitize_model(nullable_fields=_nullable_fields, optional_fields=_optional_fields,
                                        model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)

class ParentClassModel(GrandParentClassModel):

    """Implementation of the 'Parent Class' model.

    TODO: type model description here.
    NOTE: This class inherits from 'GrandParentClassModel'.

    Attributes:
        mclass (int): TODO: type description here.
        precision (float): TODO: type description here.
        big_decimal (float): TODO: type description here.
        parent_optional_nullable_with_default_value (str): TODO: type
            description here.
        parent_optional (str): TODO: type description here.
        parent_required_nullable (str): TODO: type description here.
        parent_required (str): TODO: type description here.

    """

    parent_required_nullable: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("parent_required_nullable", "Parent_Required_Nullable"),
              serialization_alias="Parent_Required_Nullable")
    ]
    mclass: Annotated[
        Optional[int],
        Field(validation_alias=AliasChoices("mclass", "class"),
              serialization_alias="class")
    ] = 23
    precision: Annotated[
        Optional[float],
        Field(validation_alias=AliasChoices("precision", "precision"),
              serialization_alias="precision")
    ] = None
    big_decimal: Annotated[
        Optional[float],
        Field(validation_alias=AliasChoices("big_decimal", "Big_Decimal"),
              serialization_alias="Big_Decimal")
    ] = None
    parent_optional_nullable_with_default_value: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("parent_optional_nullable_with_default_value", "Parent_Optional_Nullable_With_Default_Value"),
              serialization_alias="Parent_Optional_Nullable_With_Default_Value")
    ] = 'Has default value'
    parent_optional: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("parent_optional", "Parent_Optional"),
              serialization_alias="Parent_Optional")
    ] = None
    parent_required: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("parent_required", "Parent_Required"),
              serialization_alias="Parent_Required")
    ] = 'not nullable and required'

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _nullable_fields = {
            'mclass', 'precision', 'big_decimal', 'parent_optional_nullable_with_default_value',
            'parent_required_nullable', 'grand_parent_required_nullable'
        }
        _optional_fields = {
            'mclass', 'precision', 'big_decimal', 'parent_optional_nullable_with_default_value', 'parent_optional',
            'grand_parent_optional'
        }

        return ApiHelper.sanitize_model(nullable_fields=_nullable_fields, optional_fields=_optional_fields,
                                        model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)

class ChildClassModel(ParentClassModel):

    """Implementation of the 'Child Class' model.

    TODO: type model description here.
    NOTE: This class inherits from 'ParentClassModel'.

    Attributes:
        optional_nullable (str): TODO: type description here.
        optional_nullable_with_default_value (str): TODO: type description
            here.
        optional (str): TODO: type description here.
        required_nullable (str): TODO: type description here.
        required (str): TODO: type description here.
        child_class_array (List[ChildClassModel]): TODO: type description here.

    """

    required_nullable: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("required_nullable", "Required_Nullable"),
              serialization_alias="Required_Nullable")
    ]
    required : Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("required", "Required"),
              serialization_alias="Required")
    ] = 'not nullable and required'
    optional_nullable: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("optional_nullable", "Optional_Nullable"),
              serialization_alias="Optional_Nullable")
    ] = None
    optional_nullable_with_default_value: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("optional_nullable_with_default_value", "Optional_Nullable_With_Default_Value"),
              serialization_alias="Optional_Nullable_With_Default_Value")
    ] = 'With default value'
    optional: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("optional", "Optional"),
              serialization_alias="Optional")
    ] = None
    child_class_array: Annotated[
        Optional[List['ChildClassModel']],
        Field(validation_alias=AliasChoices("child_class_array", "Child_Class_Array"),
              serialization_alias="Child_Class_Array")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _nullable_fields = {
            'optional_nullable', 'optional_nullable_with_default_value', 'required_nullable', 'child_class_array',
            'mclass', 'precision', 'big_decimal', 'parent_optional_nullable_with_default_value',
            'parent_required_nullable', 'grand_parent_required_nullable'
        }
        _optional_fields = {
            'optional_nullable', 'optional_nullable_with_default_value', 'optional', 'child_class_array',
            'mclass', 'precision', 'big_decimal', 'parent_optional_nullable_with_default_value', 'parent_optional',
            'grand_parent_optional'
        }

        return ApiHelper.sanitize_model(nullable_fields=_nullable_fields, optional_fields=_optional_fields,
                                        model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)

class Child2ClassModel(ParentClassModel):

    """Implementation of the 'Child2 Class' model.

    TODO: type model description here.
    NOTE: This class inherits from 'ParentClassModel'.

    Attributes:
        optional (str): TODO: type description here.
        required_nullable (str): TODO: type description here.
        required (str): TODO: type description here.

    """

    required_nullable: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("required_nullable", "Required_Nullable"),
              serialization_alias="Required_Nullable")
    ]
    required: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("required", "Required"),
              serialization_alias="Required")
    ] = 'not nullable and required'
    optional: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("optional", "Optional"),
              serialization_alias="Optional")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _nullable_fields = {
            'required_nullable', 'mclass', 'precision', 'big_decimal', 'parent_optional_nullable_with_default_value',
            'parent_required_nullable', 'grand_parent_required_nullable'
        }
        _optional_fields = {
            'optional', 'mclass', 'precision', 'big_decimal', 'parent_optional_nullable_with_default_value',
            'parent_optional', 'grand_parent_optional'
        }

        return ApiHelper.sanitize_model(nullable_fields=_nullable_fields, optional_fields=_optional_fields,
                                        model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)