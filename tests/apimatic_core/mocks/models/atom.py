from typing import Optional

from pydantic import BaseModel, model_serializer, Field, AliasChoices
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Annotated

from apimatic_core.utilities.api_helper import ApiHelper


class Atom(BaseModel):

    """Implementation of the 'Atom' model.

    TODO: type model description here.

    Attributes:
        atom_number_of_electrons (int): TODO: type description here.
        atom_number_of_protons (int): TODO: type description here.

    """

    atom_number_of_electrons: Annotated[
        int,
        Field(validation_alias=AliasChoices("atom_number_of_electrons", "AtomNumberOfElectrons"),
              serialization_alias="AtomNumberOfElectrons")
    ]

    atom_number_of_protons: Annotated[
        Optional[int],
        Field(validation_alias=AliasChoices("atom_number_of_protons", "AtomNumberOfProtons"),
              serialization_alias="AtomNumberOfProtons")
    ] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"atom_number_of_protons"}

        return ApiHelper.sanitize_model(optional_fields=_optional_fields, model_dump=nxt(self),
                                        model_fields=self.model_fields, model_fields_set=self.model_fields_set)
