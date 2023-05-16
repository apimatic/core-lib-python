from apimatic_core.types.datetime_format import DateTimeFormat


class UnionTypeContext:

    def __init__(self):
        self._is_array: bool = False
        self._is_dict: bool = False
        self._is_array_of_dict: bool = False
        self._is_optional: bool = False
        self._is_nullable: bool = False
        self._discriminator: str | None = None
        self._discriminator_values: [] = []
        self._date_time_format: DateTimeFormat | None = None

    def array(self, is_array: bool):
        self._is_array = is_array
        return self

    def is_array(self):
        return self._is_array

    def dict(self, is_dict: bool):
        self._is_dict = is_dict
        return self

    def is_dict(self):
        return self._is_dict

    def array_of_dict(self, is_array_of_dict: bool):
        self._is_array_of_dict = is_array_of_dict
        return self

    def is_array_of_dict(self):
        return self._is_array_of_dict

    def optional(self, is_optional: bool):
        self._is_optional = is_optional
        return self

    def is_optional(self):
        return self._is_optional

    def nullable(self, is_nullable: bool):
        self._is_nullable = is_nullable
        return self

    def is_nullable(self):
        return self._is_nullable

    def is_nullable_or_nullable(self):
        return self._is_nullable or self._is_optional

    def discriminator(self, discriminator: str):
        self._discriminator = discriminator
        return self

    def get_discriminator(self):
        return self._discriminator

    def discriminator_values(self, discriminator_values: []):
        self._discriminator_values = discriminator_values
        return self

    def get_discriminator_values(self):
        return self._discriminator_values

    def date_time_format(self, date_time_format: DateTimeFormat):
        self._date_time_format = date_time_format
        return self

    def get_date_time_format(self):
        return self._date_time_format

