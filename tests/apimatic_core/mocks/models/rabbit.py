from typing import Optional
from pydantic import BaseModel, Field, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from apimatic_core.utilities.api_helper import ApiHelper
from typing_extensions import Annotated


class Rabbit(BaseModel):
    """Implementation of the 'Rabbit' model using Pydantic.

    Attributes:
        id (str): TODO: type description here.
        weight (str): TODO: type description here.
        mtype (str): TODO: type description here.
        kind (Optional[str]): TODO: type description here.
    """

    id: Annotated[str, Field(alias="id")]
    weight: Annotated[str, Field(alias="weight")]
    mtype: Annotated[str, Field(alias="type")]
    kind: Annotated[Optional[str], Field(alias="kind")] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"kind"}
        return ApiHelper.sanitize_model(optional_fields=_optional_fields, model_dump=nxt(self),
                                        model_fields=self.model_fields, model_fields_set=self.model_fields_set)
