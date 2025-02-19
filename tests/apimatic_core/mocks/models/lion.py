from typing import Optional

from pydantic import BaseModel, AliasChoices, Field, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper


class Lion(BaseModel):

    """Implementation of the 'Lion' model.

    TODO: type model description here.

    Attributes:
        id (str): TODO: type description here.
        weight (int): TODO: type description here.
        mtype (str): TODO: type description here.
        kind (str): TODO: type description here.

    """

    id: Annotated[
        str,
        Field(validation_alias=AliasChoices("id", "id"),
              serialization_alias="id")
    ]
    weight: Annotated[
        int,
        Field(validation_alias=AliasChoices("weight", "weight"),
              serialization_alias="weight")
    ]
    mtype: Annotated[
        str,
        Field(validation_alias=AliasChoices("mtype", "type"),
              serialization_alias="type")
    ]
    kind: Annotated[
        Optional[str],
        Field(validation_alias=AliasChoices("kind", "kind"),
              serialization_alias="kind")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"kind"}

        return ApiHelper.sanitize_model(optional_fields=_optional_fields, model_dump=nxt(self),
                                        model_fields=self.model_fields, model_fields_set=self.model_fields_set)
