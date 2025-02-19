from typing import Any, Optional

from pydantic import BaseModel


class XmlAttributes(BaseModel):
    value: Any = None
    root_element_name: Optional[str] = None
    array_item_name: Optional[str] = None
