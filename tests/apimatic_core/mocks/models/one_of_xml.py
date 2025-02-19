from typing import Optional, Union, List

from pydantic import AliasChoices, Field, BaseModel
from typing_extensions import Annotated
import xml.etree.ElementTree as ET
from apimatic_core.utilities.xml_helper import XmlHelper
from tests.apimatic_core.mocks.models.cat_model import CatModel
from tests.apimatic_core.mocks.models.dog_model import DogModel
from tests.apimatic_core.mocks.models.wolf_model import WolfModel


class OneOfXML(BaseModel):
    """Implementation of the 'CatsOrADogOrWolves' model.

    Case 3

    Attributes:
        value (CatModel | DogModel | WolfModel): TODO: type description here.

    """

    value: Annotated[
        Optional[Union[List[CatModel], DogModel, List[WolfModel]]],
        Field(AliasChoices("value", "value"), serialization_alias="value")
    ] = None

    @classmethod
    def from_element(cls, root: ET.Element) -> "OneOfXML":
        """Initialize an instance of this class using an xml.etree.Element.

        Args:
            root (string): The root xml element.

        Returns:
            object: An instance of this class.

        """
        value = XmlHelper.value_from_one_of_xml_elements(
            root,
            {
                'Cat': (CatModel, True, None),
                'Dog': (DogModel, False, None),
                'Wolf': (WolfModel, True, 'Items'),
            }
        )

        return cls(value=value)

    def to_xml_sub_element(self, root: ET.Element):
        """Convert this object to an instance of xml.etree.Element.

        Args:
            root (xml.etree.Element): The parent of this xml element.
        """
        if isinstance(self.value, list) and type(self.value[0]) is CatModel:
            XmlHelper.add_list_as_subelement(root, self.value, 'Cat')
        if type(self.value) is DogModel:
            XmlHelper.add_as_subelement(root, self.value, 'Dog')
        if isinstance(self.value, list) and type(self.value[0]) is WolfModel:
            XmlHelper.add_list_as_subelement(root, self.value, 'Wolf',
                                             wrapping_element_name='Items')
