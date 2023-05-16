
class Orbit(object):

    """Implementation of the 'Orbit' model.

    TODO: type model description here.

    Attributes:
        number_of_electrons (int): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "number_of_electrons": 'OrbitNumberOfElectrons'
    }

    def __init__(self,
                 number_of_electrons=None):
        """Constructor for the Orbit class"""

        # Initialize members of the class
        self.number_of_electrons = number_of_electrons

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

        number_of_electrons = dictionary.get("OrbitNumberOfElectrons") if dictionary.get("OrbitNumberOfElectrons") else None
        # Return an object of this model
        return cls(number_of_electrons)

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

        return dictionary.get("OrbitNumberOfElectrons") is not None
