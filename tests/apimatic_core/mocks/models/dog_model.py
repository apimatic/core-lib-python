from typing import Optional

from pydantic import BaseModel, AliasChoices, Field
from typing_extensions import Annotated
import xml.etree.ElementTree as ET
from apimatic_core.utilities.xml_helper import XmlHelper


class DogModel(BaseModel):

    """Implementation of the 'Dog' model.

    TODO: type model description here.

    Attributes:
        barks (bool): TODO: type description here.

    """

    barks: Annotated[
        Optional[bool],
        Field(AliasChoices("barks", "Barks"), serialization_alias="Barks")
    ] = None

    @classmethod
    def from_element(cls, root: ET.Element) -> "DogModel":
        """Initialize an instance of this class using an xml.etree.Element.

        Args:
            root (string): The root xml element.

        Returns:
            object: An instance of this class.

        """
        barks = XmlHelper.value_from_xml_element(root.find('Barks'), bool)

        return cls(barks=barks)

    def to_xml_sub_element(self, root: ET.Element):
        """Convert this object to an instance of xml.etree.Element.

        Args:
            root (xml.etree.Element): The parent of this xml element.
        """
        XmlHelper.add_as_subelement(root, self.barks, 'Barks')
