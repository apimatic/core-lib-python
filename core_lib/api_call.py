from core_lib.configurations.endpoint_configuration import EndpointConfiguration
from core_lib.response_handler import ResponseHandler


class ApiCall:

    @property
    def new_builder(self):
        return ApiCall(self.global_configuration)

    def __init__(
            self,
            global_configuration
    ):
        self.global_configuration = global_configuration
        self.request_builder = None
        self.response_handler = ResponseHandler()
        self.endpoint_configuration = EndpointConfiguration()

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
        _http_request = self.request_builder.build(self.global_configuration)
        _http_client_configuration = self.global_configuration.get_http_client_configuration()
        _http_callback = _http_client_configuration.http_callback

        self.update_http_callback_with_request(_http_callback, _http_client_configuration, _http_request)

        _http_response = _http_client_configuration.http_client.execute(
            _http_request,self.endpoint_configuration)

        self.update_http_callback_with_response(_http_callback, _http_client_configuration, _http_response)

        return self.response_handler.handle(_http_response, self.global_configuration.get_global_errors())

    def update_http_callback_with_request(self, _http_callback, _http_client_configuration, _http_request):
        if _http_callback:
            _http_client_configuration.http_callback.on_before_request(_http_request)

    def update_http_callback_with_response(self, _http_callback, _http_client_configuration, _http_response):
        if _http_callback:
            _http_client_configuration.http_callback.on_after_response(_http_response)
