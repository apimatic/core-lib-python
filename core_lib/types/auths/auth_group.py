from core_interfaces.types.authentication import Authentication

from core_lib.types.auths.auth_group_type import AuthGroupType


class AuthGroup(Authentication):

    @staticmethod
    def or_(*auth_group):
        return AuthGroup(auth_group, auth_group_type=AuthGroupType.OR)

    @staticmethod
    def and_(*auth_group):
        return AuthGroup(auth_group, auth_group_type=AuthGroupType.AND)

    @staticmethod
    def single(auth):
        return AuthGroup(auth, auth_group_type=AuthGroupType.SINGLE)

    def __init__(self, auth_group, auth_group_type):
        self._auth_group = auth_group
        self._auth_group_type = auth_group_type
        self._auths = []
        self._is_valid = True
        self._error_messages = []

    def with_auth_managers(self, auth_managers):
        if self._auth_group_type == AuthGroupType.SINGLE:
            self._auths.append(auth_managers[self._auth_group])
        else:
            for group in self._auth_group:
                if isinstance(group, str) and auth_managers.get(group):
                    self._auths.append(auth_managers[group])
                elif isinstance(group, AuthGroup):
                    self._auths.append(group.with_auth_managers(auth_managers))
                else:
                    raise ValueError("Auth key is invalid.")
        return self

    def validate(self):
        for auth in self._auths:
            if AuthGroupType.SINGLE == self._auth_group_type:
                if not auth.validate():
                    self._error_messages.append(auth.error_message())
                    self._is_valid = False
            if AuthGroupType.OR == self._auth_group_type:
                if not auth.validate():
                    self._error_messages.append(auth.error_message())
                    self._is_valid = False
                else:
                    self._is_valid = True
                    break
            elif AuthGroupType.AND == self._auth_group_type:
                if not auth.validate():
                    self._error_messages.append(auth.error_message())
                    self._is_valid = False
        if not self._is_valid:
            raise PermissionError("Required authentication is missing for: " + " and ".join(self._error_messages))

    def apply(self, http_request):
        """ Add OAuth2 authentication to the request.

            http_request (HttpRequest): The HttpRequest object to which
                authentication header will be added.

        """
        if not self._is_valid:
            return

        for auth in self._auths:
            auth.apply(http_request)

