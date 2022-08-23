from enum import Enum


class AuthGroupType(Enum):
    """Enumeration of AuthGroup types

    Attributes:
        AND: For combining multiple auth using AND
        OR: For combining multiple auth using OR
        SINGLE: For single auth only
    """

    AND = "AND"

    OR = "OR"

    SINGLE = "SINGLE"
