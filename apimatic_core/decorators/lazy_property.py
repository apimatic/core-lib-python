from typing import Callable, Optional, Type
from pydantic import Field, validate_call

class LazyProperty:
    """A decorator class for lazy instantiation."""

    f_get: Callable[[object], object] = Field(...)
    func_name: str = Field(...)

    @validate_call
    def __init__(self, f_get: Callable[[object], object]):
        self.f_get = f_get
        self.func_name = f_get.__name__

    def __get__(self, obj: Optional[object], cls: Optional[Type[object]]) -> Optional[object]:
        if obj is None:
            return None
        value = self.f_get(obj)
        setattr(obj, self.func_name, value)
        return value