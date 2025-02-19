from typing import Optional

from pydantic import AliasChoices, Field, BaseModel
from typing_extensions import Annotated
import xml.etree.ElementTree as ET
from apimatic_core.utilities.xml_helper import XmlHelper


class WolfModel(BaseModel):

    """Implementation of the 'Wolf' model.

    TODO: type model description here.

    Attributes:
        howls (bool): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "howls": 'Howls'
    }

    howls: Annotated[
        Optional[bool],
        Field(AliasChoices("howls", "Howls"), serialization_alias="Howls")
    ] = None

    @classmethod
    def from_element(cls, root: ET.Element) -> "WolfModel":
        """Initialize an instance of this class using an xml.etree.Element.

        Args:
            root (string): The root xml element.

        Returns:
            object: An instance of this class.

        """
        howls = XmlHelper.value_from_xml_element(root.find('Howls'), bool)

        return cls(howls=howls)

    def to_xml_sub_element(self, root: ET.Element):
        """Convert this object to an instance of xml.etree.Element.

        Args:
            root (xml.etree.Element): The parent of this xml element.
        """
        XmlHelper.add_as_subelement(root, self.howls, 'Howls')
