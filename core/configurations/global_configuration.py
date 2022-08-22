
class GlobalConfiguration:

    @property
    def client_configuration(self):
        return self.client_configuration

    @property
    def error_cases(self):
        return self.error_cases

    @property
    def auth_managers(self):
        return self.auth_managers

    @property
    def user_agent(self):
        return self.user_agent

    @property
    def headers(self):
        return self.headers

    @property
    def server_urls(self):
        return self.server_urls

    @property
    def default_server(self):
        return self.default_server

    def __init__(
            self, client_configuration
    ):
        self.client_configuration = client_configuration

