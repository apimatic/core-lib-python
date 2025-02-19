from pydantic import BaseModel, Field, AliasChoices, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper


class Orbit(BaseModel):

    """Implementation of the 'Orbit' model.

    TODO: type model description here.

    Attributes:
        orbit_number_of_electrons (int): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "orbit_number_of_electrons": 'OrbitNumberOfElectrons'
    }

    orbit_number_of_electrons: Annotated[
        int,
        Field(validation_alias=AliasChoices("orbit_number_of_electrons", "OrbitNumberOfElectrons"),
              serialization_alias="OrbitNumberOfElectrons")
    ]

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        return ApiHelper.sanitize_model(model_dump=nxt(self), model_fields=self.model_fields,
                                        model_fields_set=self.model_fields_set)
