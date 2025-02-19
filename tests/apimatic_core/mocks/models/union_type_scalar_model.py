from typing import Optional, Union
from pydantic import BaseModel, Field, model_serializer, AliasChoices
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from apimatic_core.utilities.api_helper import ApiHelper
from typing_extensions import Annotated


class UnionTypeScalarModel(BaseModel):
    """Implementation of the 'ScalarModel' model using Pydantic.

    This class contains scalar types in oneOf/anyOf cases.

    Attributes:
        any_of_required (Union[float, bool]): TODO: type description here.
        one_of_req_nullable (Optional[Union[int, str]]): TODO: type description here.
        one_of_optional (Optional[Union[int, float, str]]): TODO: type description here.
        any_of_opt_nullable (Optional[Union[int, bool]]): TODO: type description here.
    """

    any_of_required: Annotated[
        Union[float, bool],
        Field(validation_alias=AliasChoices("any_of_required", "anyOfRequired"),
              serialization_alias="anyOfRequired")
    ]
    one_of_req_nullable: Annotated[
        Optional[Union[int, str]],
        Field(validation_alias=AliasChoices("one_of_req_nullable", "oneOfReqNullable"),
              serialization_alias="oneOfReqNullable")
    ]
    one_of_optional: Annotated[
        Optional[Union[int, float, str]],
        Field(validation_alias=AliasChoices("one_of_optional", "oneOfOptional"),
              serialization_alias="oneOfOptional")
    ] = None
    any_of_opt_nullable: Annotated[
        Optional[Union[int, bool]],
        Field(validation_alias=AliasChoices("any_of_opt_nullable", "anyOfOptNullable"),
              serialization_alias="anyOfOptNullable")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"one_of_optional", "any_of_opt_nullable"}
        _nullable_fields = {"one_of_req_nullable", "any_of_opt_nullable"}
        return ApiHelper.sanitize_model(nullable_fields= _nullable_fields, optional_fields=_optional_fields,
                                        model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)
