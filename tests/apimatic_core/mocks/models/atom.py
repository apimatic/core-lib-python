from apimatic_core.utilities.api_helper import ApiHelper


class Atom(object):
    """Implementation of the 'Atom' model.

    TODO: type model description here.

    Attributes:
        number_of_electrons (int): TODO: type description here.
        number_of_protons (int): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "number_of_electrons": 'AtomNumberOfElectrons', # int, bool
        "number_of_protons": 'AtomNumberOfProtons'
    }

    _optionals = [
        'number_of_protons',
    ]

    def __init__(self,
                 number_of_electrons=None,
                 number_of_protons=ApiHelper.SKIP):
        """Constructor for the Atom class"""

        # Initialize members of the class
        self.number_of_electrons = number_of_electrons
        if number_of_protons is not ApiHelper.SKIP:
            self.number_of_protons = number_of_protons

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

        number_of_electrons = dictionary.get("AtomNumberOfElectrons") if dictionary.get("AtomNumberOfElectrons") else None
        number_of_protons = dictionary.get("AtomNumberOfProtons") if dictionary.get("AtomNumberOfProtons") else ApiHelper.SKIP
        # Return an object of this model
        return cls(number_of_electrons,
                   number_of_protons)

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

        return dictionary.get("AtomNumberOfElectrons") is not None
