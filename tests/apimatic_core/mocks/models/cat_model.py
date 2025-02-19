from typing import Optional

from pydantic import AliasChoices, Field, BaseModel
from typing_extensions import Annotated
import xml.etree.ElementTree as ET
from apimatic_core.utilities.xml_helper import XmlHelper


class CatModel(BaseModel):

    """Implementation of the 'Cat' model.

    TODO: type model description here.

    Attributes:
        meows (bool): TODO: type description here.

    """

    meows: Annotated[
        Optional[bool],
        Field(AliasChoices("meows", "Meows"), serialization_alias="Meows")
    ] = None

    @classmethod
    def from_element(cls, root: ET.Element) -> "CatModel":
        """Initialize an instance of this class using an xml.etree.Element.

        Args:
            root (string): The root xml element.

        Returns:
            object: An instance of this class.

        """
        meows = XmlHelper.value_from_xml_element(root.find('Meows'), bool)

        return cls(meows=meows)

    def to_xml_sub_element(self, root: ET.Element):
        """Convert this object to an instance of xml.etree.Element.

        Args:
            root (xml.etree.Element): The parent of this xml element.
        """
        XmlHelper.add_as_subelement(root, self.meows, 'Meows')
