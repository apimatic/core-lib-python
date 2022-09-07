
class Parameter:

    @property
    def get_key(self):
        return self._key

    @property
    def get_value(self):
        return self._value

    @property
    def needs_encoding(self):
        return self._should_encode

    def __init__(
            self
    ):
        self._key = None
        self._value = None
        self._is_required = False
        self._should_encode = False

    def key(self, key):
        self._key = key
        return self

    def value(self, value):
        self._value = value
        return self

    def is_required(self, is_required):
        self._is_required = is_required
        return self

    def should_encode(self, should_encode):
        self._should_encode = should_encode
        return self

    def validate(self):
        if self._is_required and self._value is None:
            raise ValueError("Required parameter {} cannot be None.".format(self._key))

