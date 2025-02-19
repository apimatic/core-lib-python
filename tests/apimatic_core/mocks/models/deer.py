from pydantic import model_serializer, BaseModel, AliasChoices, Field
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper


class Deer(BaseModel):

    """Implementation of the 'Deer' model.

    TODO: type model description here.

    Attributes:
        name (str): TODO: type description here.
        weight (int): TODO: type description here.
        mtype (str): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name": 'name',
        "weight": 'weight',
        "mtype": 'type'
    }

    name: Annotated[
        str,
        Field(validation_alias=AliasChoices("name", "name"),
              serialization_alias="name")
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

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        return ApiHelper.sanitize_model(model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)
