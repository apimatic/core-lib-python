from abc import abstractmethod

from apimatic_core_interfaces.authentication.authentication import Authentication
from apimatic_core_interfaces.http.http_request import HttpRequest
from pydantic import validate_call
from typing import Union, List, Dict, Tuple

from apimatic_core.authentication.multiple.single_auth import Single


class AuthGroup(Authentication):

    @property
    @abstractmethod
    def error_message(self) -> str:
        ...

    @property
    def auth_participants(self) -> List[Authentication]:
        return self._auth_participants

    @property
    def mapped_group(self) -> List[Authentication]:
        return self._mapped_group

    @property
    def error_messages(self) -> List[str]:
        return self._error_messages

    @property
    def is_valid_group(self) -> bool:
        return self._is_valid_group

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, auth_group: Tuple[Union[str, Authentication], ...]):
        self._auth_participants: List[Authentication] = []
        for auth_participant in auth_group:
            if auth_participant is not None and isinstance(auth_participant, str):
                self._auth_participants.append(Single(auth_participant))
            elif auth_participant is not None:
                self._auth_participants.append(auth_participant)

        self._mapped_group: List[Authentication] = []
        self._error_messages: List[str] = []
        self._is_valid_group: bool = False

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def with_auth_managers(self, auth_managers: Dict[str, Authentication]) -> 'Authentication':
        for participant in self.auth_participants:
            self.mapped_group.append(participant.with_auth_managers(auth_managers))

        return self

    @validate_call
    @abstractmethod
    def is_valid(self) -> bool:  # pragma: no cover
        ...

    @validate_call
    def apply(self, http_request: HttpRequest):
        if not self.is_valid_group:
            return

        for participant in self.mapped_group:
            participant.apply(http_request)
