from typing import Optional, List
from pydantic import BaseModel, Field, AliasChoices
from typing_extensions import Annotated


class InnerComplexType(BaseModel):
    """Implementation of the 'InnerComplexType' model using Pydantic.

    Attributes:
        string_type (str): TODO: type description here.
        boolean_type (bool): TODO: type description here.
        long_type (int): TODO: type description here.
        precision_type (float): TODO: type description here.
        string_list_type (list[str]): TODO: type description here.
    """

    string_type: Annotated[
        Optional[str],
        Field(AliasChoices("string_type", "stringType"), serialization_alias="stringType")
    ] = None
    boolean_type: Annotated[
        Optional[bool],
        Field(AliasChoices("boolean_type", "booleanType"), serialization_alias="booleanType")
    ] = None
    long_type: Annotated[
        Optional[int],
        Field(AliasChoices("long_type", "longType"), serialization_alias="longType")
    ] = None
    precision_type: Annotated[
        Optional[float],
        Field(AliasChoices("precision_type", "precisionType"), serialization_alias="precisionType")
    ] = None
    string_list_type: Annotated[
        Optional[List[str]],
        Field(AliasChoices("string_list_type", "stringListType"), serialization_alias="stringListType")
    ] = None

