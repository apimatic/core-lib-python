from apimatic_core_interfaces.types.authentication import Authentication


class QueryAuth(Authentication):

    def __init__(self, auth_params):
        self._auth_params = auth_params

    def is_valid(self):
        return self._auth_params and all(param and self._auth_params[param] for param in self._auth_params)

    def apply(self, http_request):
        for param in self._auth_params:
            http_request.add_query_parameter(param, self._auth_params[param])
