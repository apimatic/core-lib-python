from apimatic_core_interfaces.types.authentication import Authentication


class HeaderAuth(Authentication):

    def __init__(self, auth_params):
        self._auth_params = auth_params
        self._error_message = None

    def is_valid(self):
        return self._auth_params and all(param and self._auth_params[param] for param in self._auth_params)

    def apply(self, http_request):
        for param in self._auth_params:
            http_request.add_header(param, self._auth_params[param])

