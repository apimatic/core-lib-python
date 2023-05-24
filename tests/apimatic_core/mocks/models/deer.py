class Deer(object):
    """Implementation of the 'Deer' model.

    TODO: type model description here.

    Attributes:
        name (string): TODO: type description here.
        weight (string): TODO: type description here.
        mtype (string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name": 'name',
        "weight": 'weight',
        "mtype": 'type'
    }

    def __init__(self,
                 name=None,
                 weight=None,
                 mtype=None):
        """Constructor for the Deer class"""

        # Initialize members of the class
        self.name = name
        self.weight = weight
        self.mtype = mtype

    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object
            as obtained from the deserialization of the server's response. The
            keys MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary

        name = dictionary.get("name") if dictionary.get("name") else None
        weight = dictionary.get("weight") if dictionary.get("weight") else None
        mtype = dictionary.get("type") if dictionary.get("type") else None
        # Return an object of this model
        return cls(name,
                   weight,
                   mtype)

    @classmethod
    def validate(cls, dictionary):
        """Validates dictionary against class properties.

        Args:
            dictionary: the dictionary to be validated against.

        Returns:
            boolean : if value is valid for this model.

        """
        if dictionary is None:
            return None

        return dictionary.get("name") is not None and \
               dictionary.get("weight") is not None and \
               dictionary.get("type") is not None
