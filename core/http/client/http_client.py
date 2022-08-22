# -*- coding: utf-8 -*-


class HttpClient(object):
    """An interface for the methods that an HTTP Client must implement

    This class should not be instantiated but should be used as a base class
    for HTTP Client classes.

    """

    def execute(self, request, endpoint_configuration):
        """Execute a given CoreHttpRequest to get a string response back

        Args:
            request (HttpRequest): The given HttpRequest to execute.
            endpoint_configuration (EndpointConfiguration): The endpoint configurations to use.

        Returns:
            HttpResponse: The response of the CoreHttpRequest.

        """
        raise NotImplementedError("Please Implement this method")

    def convert_response(self, response, is_binary_response):
        """Converts the Response object of the HttpClient into an
        HttpResponse object.

        Args:
            response (dynamic): The original response object.
            is_binary_response (bool): The flag to check if the response is of binary type.

        Returns:
            HttpResponse: The converted HttpResponse object.

        """
        raise NotImplementedError("Please Implement this method")
