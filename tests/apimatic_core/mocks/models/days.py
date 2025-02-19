from enum import Enum
from typing import Optional


class Days(str, Enum):

    """Implementation of the 'Days' enum.

    A string enum representing days of the week

    Attributes:
        SUNDAY: TODO: type description here.
        MONDAY: TODO: type description here.
        TUESDAY: TODO: type description here.
        WEDNESDAY_: TODO: type description here.
        THURSDAY: TODO: type description here.
        FRI DAY: TODO: type description here.
        SATURDAY: TODO: type description here.

    """

    SUNDAY = 'Sunday'

    MONDAY = 'Monday'

    TUESDAY = 'Tuesday'

    WEDNESDAY_ = 'Wednesday'

    THURSDAY = 'Thursday'

    FRI_DAY = 'Friday'

    SATURDAY = 'Saturday'

    @classmethod
    def is_valid(cls, value: Optional[str]) -> bool:
        return value in cls._value2member_map_
