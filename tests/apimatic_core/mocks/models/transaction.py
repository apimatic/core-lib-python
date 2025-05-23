from apimatic_core.utilities.api_helper import ApiHelper


class Transaction(object):

    """Implementation of the 'Transaction' model.

    Attributes:
        id (str): The model property of type str.
        amount (float): The model property of type float.
        timestamp (datetime): The model property of type datetime.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id": 'id',
        "amount": 'amount',
        "timestamp": 'timestamp'
    }

    _optionals = [
        'id',
        'amount',
        'timestamp',
    ]

    def __init__(self,
                 id=ApiHelper.SKIP,
                 amount=ApiHelper.SKIP,
                 timestamp=ApiHelper.SKIP):
        """Constructor for the Transaction class"""

        # Initialize members of the class
        if id is not ApiHelper.SKIP:
            self.id = id 
        if amount is not ApiHelper.SKIP:
            self.amount = amount 
        if timestamp is not ApiHelper.SKIP:
            self.timestamp = ApiHelper.apply_datetime_converter(timestamp, ApiHelper.HttpDateTime) if timestamp else None

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

        if not isinstance(dictionary, dict) or dictionary is None:
            return None

        # Extract variables from the dictionary
        id = dictionary.get("id") if dictionary.get("id") else ApiHelper.SKIP
        amount = dictionary.get("amount") if dictionary.get("amount") else ApiHelper.SKIP
        timestamp = ApiHelper.HttpDateTime.from_value(dictionary.get("timestamp")).datetime if dictionary.get("timestamp") else ApiHelper.SKIP
        # Return an object of this model
        return cls(id,
                   amount,
                   timestamp)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'id={(self.id if hasattr(self, "id") else None)!r}, '
                f'amount={(self.amount if hasattr(self, "amount") else None)!r}, '
                f'timestamp={(self.timestamp if hasattr(self, "timestamp") else None)!r})')

    def __str__(self):
        return (f'{self.__class__.__name__}('
                f'id={(self.id if hasattr(self, "id") else None)!s}, '
                f'amount={(self.amount if hasattr(self, "amount") else None)!s}, '
                f'timestamp={(self.timestamp if hasattr(self, "timestamp") else None)!s})')
