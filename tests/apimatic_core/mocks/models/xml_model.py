from apimatic_core.utilities.xml_helper import XmlHelper
import xml.etree.ElementTree as ET

from typing import Optional
from pydantic import BaseModel, Field, AliasChoices
from typing_extensions import Annotated


class XMLModel(BaseModel):
    """Implementation of the 'AttributesAndElements' model using Pydantic.

    Attributes:
        string_attr (str): string attribute (attribute name "string")
        number_attr (int): number attribute (attribute name "number")
        boolean_attr (Optional[bool]): boolean attribute (attribute name "boolean")
        string_element (str): string element (element name "string")
        number_element (int): number element (element name "number")
        boolean_element (Optional[bool]): boolean element (element name "boolean")
        elements (Optional[list]): Additional elements.
    """

    string_attr: Annotated[
        Optional[str],
        Field(AliasChoices("string_attr", "string-attr"), serialization_alias="string-attr")
    ] = None
    number_attr: Annotated[
        Optional[int],
        Field(AliasChoices("number_attr", "number-attr"), serialization_alias="number-attr")
    ] = None
    boolean_attr: Annotated[
        Optional[bool],
        Field(AliasChoices("boolean_attr", "boolean-attr"), serialization_alias="boolean-attr")
    ] = None
    string_element: Annotated[
        Optional[str],
        Field(AliasChoices("string_element", "string-element"), serialization_alias="string-element")
    ] = None
    number_element: Annotated[
        Optional[int],
        Field(AliasChoices("number_element", "number-element"), serialization_alias="number-element")
    ] = None
    boolean_element: Annotated[
        Optional[bool],
        Field(AliasChoices("boolean_element", "boolean-element"), serialization_alias="boolean-element")
    ] = None
    elements: Annotated[
        Optional[list],
        Field(AliasChoices("elements", "elements"), serialization_alias="elements")
    ] = None

    @classmethod
    def from_element(cls, root: ET.Element) -> 'XMLModel':
        """Initialize an instance of this class using an xml.etree.Element.

        Args:
            root (string): The root xml element.

        Returns:
            object: An instance of this class.

        """
        string_attr = XmlHelper.value_from_xml_attribute(root.get('string'), str)
        number_attr = XmlHelper.value_from_xml_attribute(root.get('number'), int)
        boolean_attr = XmlHelper.value_from_xml_attribute(root.get('boolean'), bool)
        string_element = XmlHelper.value_from_xml_element(root.find('string'), str)
        number_element = XmlHelper.value_from_xml_element(root.find('number'), int)
        boolean_element = XmlHelper.value_from_xml_element(root.find('boolean'), bool)
        elements = XmlHelper.list_from_xml_element(
            root, 'item', str, wrapping_element_name='elements')
        return cls(string_attr=string_attr,
                   number_attr=number_attr,
                   boolean_attr=boolean_attr,
                   string_element=string_element,
                   number_element=number_element,
                   boolean_element=boolean_element,
                   elements=elements)

    def to_xml_sub_element(self, root: ET.Element):
        """Convert this object to an instance of xml.etree.Element.

        Args:
            root (xml.etree.Element): The parent of this xml element.
        """
        XmlHelper.add_as_attribute(root, self.string_attr, 'string')
        XmlHelper.add_as_attribute(root, self.number_attr, 'number')
        XmlHelper.add_as_attribute(root, self.boolean_attr, 'boolean')
        XmlHelper.add_as_subelement(root, self.string_element, 'string')
        XmlHelper.add_as_subelement(root, self.number_element, 'number')
        XmlHelper.add_as_subelement(root, self.boolean_element, 'boolean')
        XmlHelper.add_list_as_subelement(root, self.elements, 'item',
                                         wrapping_element_name='elements')
