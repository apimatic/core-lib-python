from enum import Enum
class Days(Enum):

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
    def validate(cls, value):
        """Validates value against enum.

        Args:
            value: the value to be validated against.

        Returns:
            boolean : if value is valid for this model.

        """
        if value is None:
            return None

        values = [member.value for member in Days]
        return value in values