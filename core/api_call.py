class ApiCall:

    def __init__(
            self,
            global_configuration
    ):
        self.global_configuration = global_configuration

    def new_builder(self):
        return ApiCall(self.global_configuration)

    def request(self, request_builder):
        self.request_builder = request_builder
        return self

    def response(self, response_handler):
        self.response_handler = response_handler
        return self

    def configuration(self, endpoint_configuration):
        self.endpoint_configuration = endpoint_configuration
        return self

    def execute(self):
        pass
