# -*- coding: utf-8 -*-
from typing import Optional, Dict, List, Union, Any

from pydantic import BaseModel, Field, AliasChoices, model_validator, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Annotated

from tests.apimatic_core.mocks.models.lion import Lion
from apimatic_core.utilities.api_helper import ApiHelper


class ModelWithAdditionalPropertiesOfPrimitiveType(BaseModel):

    """Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, int]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}


class ModelWithAdditionalPropertiesOfPrimitiveArrayType(BaseModel):

    """"Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, List[int]]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}

class ModelWithAdditionalPropertiesOfPrimitiveDictType(BaseModel):

    """Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, Dict[str, int]]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}

class ModelWithAdditionalPropertiesOfModelType(BaseModel):

    """Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, Lion]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}

class ModelWithAdditionalPropertiesOfModelArrayType(BaseModel):

    """Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, List[Lion]]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}

class ModelWithAdditionalPropertiesOfModelDictType(BaseModel):

    """Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, Dict[str, Lion]]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}

class ModelWithAdditionalPropertiesOfTypeCombinatorPrimitive(BaseModel):

    """Implementation of the 'NonInheritEnabledNumber' model.

    TODO: type model description here.

    Attributes:
        email (str): TODO: type description here.

    """

    email: Annotated[
        str,
        Field(validation_alias=AliasChoices("email", "email"),
              serialization_alias="email")
    ]

    additional_properties: Optional[Dict[str, Union[float, bool]]] = None

    @model_validator(mode="before")
    def populate_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all extra fields and move them into `additional_properties`.
        Raise ValueError if an additional property has a name similar to a model property.

        Args:
            values (Dict[str, Any]): The input data for the model.

        Returns:
            Dict[str, Any]: The modified data with additional properties populated.
        """
        additional_props_field = "additional_properties"

        if isinstance(values.get(additional_props_field), dict):
            ApiHelper.check_conflicts_with_additional_properties(
                cls, values[additional_props_field], additional_props_field)
            return values

        aliases = [field.serialization_alias or name for name, field in cls.model_fields.items()]

        additional_properties = {
            key: value for key, value in values.items() if key not in aliases
        }

        ApiHelper.check_conflicts_with_additional_properties(cls, additional_properties, additional_props_field)

        values[additional_props_field] = additional_properties
        return values

    @model_serializer(mode="wrap")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler):
        _optional_fields = {"additional_properties"}

        serialized_model = nxt(self)
        additional_properties = serialized_model.pop("additional_properties", {})
        sanitized_model = ApiHelper.sanitize_model(optional_fields=_optional_fields,
                                                   model_dump=serialized_model, model_fields=self.model_fields,
                                                   model_fields_set=self.model_fields_set)
        return {**sanitized_model, **(additional_properties or {})}