
class ApiCall:

    def __init__(
            self,
            global_configuration,
            request_builder,
            response_handler,
            endpoint_configuration
    ):
        self.global_configuration = global_configuration
        self.request_builder = request_builder
        self.response_handler = response_handler
        self.endpoint_configuration = endpoint_configuration

    def execute(self):
        pass

