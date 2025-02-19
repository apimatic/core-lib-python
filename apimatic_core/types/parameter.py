from typing import Any, Callable, Optional

from pydantic import BaseModel


class Parameter(BaseModel):

    key: Optional[str] = None
    value: Any = None
    is_required: bool = False
    should_encode: bool = False
    default_content_type: Optional[str] = None
    validator: Optional[Callable[[Any], bool]] = None

    def is_valid_parameter(self):
        if self.is_required and self.value is None:
            raise ValueError("Required parameter {} cannot be None.".format(self.key))

        if self.validator is None:
            return True

        return self.validator(self.value)

