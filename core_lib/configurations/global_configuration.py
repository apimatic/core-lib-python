
class GlobalConfiguration:

    def get_http_client_configuration(self):
        return self._http_client_configuration

    def get_global_errors(self):
        return self._global_errors

    def get_global_headers(self):
        return self._global_headers

    def get_auth_managers(self):
        return self._auth_managers

    def get_user_agent(self):
        return self._user_agent

    def get_base_uri(self, server):
        return self._base_uri_executor(server)

    def __init__(
            self, http_client_configuration
    ):
        self._http_client_configuration = http_client_configuration
        self._global_errors = None
        self._global_headers = {}
        self._auth_managers = None
        self._user_agent = None
        self._base_uri_executor = None

    def global_errors(self, global_errors):
        self._global_errors = global_errors
        return self

    def global_headers(self, global_headers):
        self._global_headers = global_headers
        return self

    def global_header(self, key, value):
        self._global_headers[key] = value
        return self

    def auth_managers(self, auth_managers):
        self._auth_managers = auth_managers
        return self

    def user_agent(self, user_agent):
        self._user_agent = user_agent
        return self

    def base_uri_executor(self, base_uri_executor):
        self._base_uri_executor = base_uri_executor
        return self
