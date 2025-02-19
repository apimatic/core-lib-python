from typing import Optional
from pydantic import BaseModel, Field, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from apimatic_core.utilities.api_helper import ApiHelper
from typing_extensions import Annotated


class Validate(BaseModel):
    """Implementation of the 'Validate' model using Pydantic.

    Attributes:
        field (str): TODO: type description here.
        name (str): TODO: type description here.
        address (Optional[str]): TODO: type description here.
    """

    field: Annotated[str, Field(alias="field")]
    name: Annotated[str, Field(alias="name")]
    address: Annotated[Optional[str], Field(alias="address")] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"address"}
        return ApiHelper.sanitize_model(optional_fields=_optional_fields, model_dump=nxt(self),
                                        model_fields=self.model_fields, model_fields_set=self.model_fields_set)
