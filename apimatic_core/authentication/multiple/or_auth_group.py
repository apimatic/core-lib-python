from apimatic_core_interfaces.authentication.authentication import Authentication
from typing import Union

from pydantic import validate_call

from apimatic_core.authentication.multiple.auth_group import AuthGroup


class Or(AuthGroup):

    @property
    def error_message(self) -> str:
        return " or ".join(self._error_messages)

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, *auth_group: Union[str, Authentication]):
        super(Or, self).__init__(auth_group)
        self._is_valid_group = False

    @validate_call
    def is_valid(self) -> bool:
        if not self.mapped_group:
            return False

        for participant in self.mapped_group:
            self._is_valid_group = participant.is_valid()
            # returning as we encounter the first participant as valid
            if self._is_valid_group:
                return self._is_valid_group

            self.error_messages.append(participant.error_message)

        return self._is_valid_group

