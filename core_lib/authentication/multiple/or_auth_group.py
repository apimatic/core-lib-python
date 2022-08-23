from core_interfaces.types.authentication import Authentication
from core_lib.authentication.multiple.single_auth import Single


class Or(Authentication):

    @property
    def error_message(self):
        return " or ".join(self._error_messages)

    def __init__(self, *auth_group):
        self._auth_participants = []
        for auth_participant in auth_group:
            if isinstance(auth_participant, str):
                self._auth_participants.append(Single(auth_participant))
            else:
                self._auth_participants.append(auth_participant)

        self._mapped_group = []
        self._error_messages = []
        self._is_valid = False

    def with_auth_managers(self, auth_managers):
        for participant in self._auth_participants:
            self._mapped_group.append(participant.with_auth_managers(auth_managers))

        return self

    def is_valid(self):
        if not self._mapped_group:
            return False

        for participant in self._mapped_group:
            if participant.is_valid():
                self._is_valid = True
            else:
                self._error_messages.append(participant.error_message)

        return self._is_valid

    def apply(self, http_request):
        """ Add OAuth2 authentication to the request.

            http_request (HttpRequest): The HttpRequest object to which
                authentication header will be added.

        """

        if not self._is_valid:
            return

        for participant in self._mapped_group:
            participant.apply(http_request)

