from apimatic_core_interfaces.authentication.authentication import Authentication
from pydantic import validate_call
from typing import Union

from apimatic_core.authentication.multiple.auth_group import AuthGroup


class And(AuthGroup):

    @property
    @validate_call
    def error_message(self) -> str:
        return " and ".join(self._error_messages)

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, *auth_group: Union[str, Authentication]):
        super(And, self).__init__(auth_group)
        self._is_valid_group = True

    @validate_call
    def is_valid(self) -> bool:
        if not self.mapped_group:
            return False

        for participant in self.mapped_group:
            if not participant.is_valid():
                self.error_messages.append(participant.error_message)
                self._is_valid_group = False

        return self.is_valid_group
