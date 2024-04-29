from apimatic_core_interfaces.logger.ApiLogger import ApiLogger


class SdkLogger(ApiLogger):

    @property
    def logger(self):
        return self._logger

    def __init__(self, logger):
        self._logger = logger

    def log_request(self, http_request):
        """Logs the given HTTP request.

        Args:
            http_request (HttpRequest): The HTTP request to log.
        """
        print("Logging Request")
        pass

    def log_response(self, http_response):
        """Logs the given HTTP response.

        Args:
            http_response (HttpRequest): The HTTP request to log.
        """
        print("Logging Response")
        pass


class NoneSdkLogger(ApiLogger):

    def log_request(self, http_request):
        """Logs the given HTTP request.

        Args:
            http_request (HttpRequest): The HTTP request to log.
        """
        pass

    def log_response(self, http_response):
        """Logs the given HTTP response.

        Args:
            http_response (HttpRequest): The HTTP request to log.
        """
        pass
