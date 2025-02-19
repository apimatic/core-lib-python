from typing import Optional, List, Dict
from pydantic import BaseModel, Field, model_serializer, AliasChoices
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from apimatic_core.utilities.api_helper import ApiHelper
from typing_extensions import Annotated

from tests.apimatic_core.mocks.models.inner_complex_type import InnerComplexType


class ComplexType(BaseModel):
    """Implementation of the 'ComplexType' model using Pydantic.

    Attributes:
        inner_complex_type (InnerComplexType): TODO: type description here.
        inner_complex_list_type (list[InnerComplexType]): TODO: type description here.
        inner_complex_map_type (Optional[dict]): TODO: type description here.
        inner_complex_list_of_map_type (Optional[list[InnerComplexType]]): TODO: type description here.
        inner_complex_map_of_list_type (Optional[list[InnerComplexType]]): TODO: type description here.
    """

    inner_complex_type: Annotated[
        InnerComplexType,
        Field(validation_alias=AliasChoices("inner_complex_type", "innerComplexType"),
              serialization_alias="innerComplexType")
    ]
    inner_complex_list_type: Annotated[
        List[InnerComplexType],
        Field(validation_alias=AliasChoices("inner_complex_list_type", "innerComplexListType"),
              serialization_alias="innerComplexListType")
    ]
    inner_complex_map_type: Annotated[
        Optional[Dict],
        Field(validation_alias=AliasChoices("inner_complex_map_type", "innerComplexMapType"),
              serialization_alias="innerComplexMapType")
    ] = None
    inner_complex_list_of_map_type: Annotated[
        Optional[List[InnerComplexType]],
        Field(validation_alias=AliasChoices("inner_complex_list_of_map_type", "innerComplexListOfMapType"),
              serialization_alias="innerComplexListOfMapType")
    ] = None
    inner_complex_map_of_list_type: Annotated[
        Optional[List[InnerComplexType]],
        Field(validation_alias=AliasChoices("inner_complex_map_of_list_type", "innerComplexMapOfListType"),
              serialization_alias="innerComplexMapOfListType")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {
            "inner_complex_map_type",
            "inner_complex_list_of_map_type",
            "inner_complex_map_of_list_type"
        }
        return ApiHelper.sanitize_model(optional_fields=_optional_fields, model_dump=nxt(self),
                                        model_fields=self.model_fields, model_fields_set=self.model_fields_set)
