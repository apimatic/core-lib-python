# -*- coding: utf-8 -*-

from http.request.core_request import CoreHttpRequest

from http.core_http_method_enum import CoreHttpMethodEnum


class CoreHttpClient(object):
    """An interface for the methods that an HTTP Client must implement

    This class should not be instantiated but should be used as a base class
    for HTTP Client classes.

    """

    def execute_as_string(self, request):
        """Execute a given CoreHttpRequest to get a string response back

        Args:
            request (CoreHttpRequest): The given CoreHttpRequest to execute.

        Returns:
            HttpResponse: The response of the CoreHttpRequest.

        """
        raise NotImplementedError("Please Implement this method")

    def execute_as_binary(self, request):
        """Execute a given CoreHttpRequest to get a binary response back

        Args:
            request (CoreHttpRequest): The given CoreHttpRequest to execute.

        Returns:
            HttpResponse: The response of the CoreHttpRequest.

        """
        raise NotImplementedError("Please Implement this method")

    def convert_response(self, response, binary):
        """Converts the Response object of the HttpClient into an
        HttpResponse object.

        Args:
            response (dynamic): The original response object.

        Returns:
            HttpResponse: The converted HttpResponse object.

        """
        raise NotImplementedError("Please Implement this method")

    def get(self, query_url,
            headers={},
            query_parameters={}):
        """Create a simple GET CoreHttpRequest object for the given parameters

        Args:
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.

        Returns:
            CoreHttpRequest: The generated CoreHttpRequest for the given paremeters.

        """
        return CoreHttpRequest(CoreHttpMethodEnum.GET,
                               query_url,
                               headers,
                               query_parameters,
                               None,
                               None)

    def head(self, query_url,
             headers={},
             query_parameters={}):
        """Create a simple HEAD CoreHttpRequest object for the given parameters

        Args:
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.

        Returns:
            CoreHttpRequest: The generated CoreHttpRequest for the given paremeters.

        """
        return CoreHttpRequest(CoreHttpMethodEnum.HEAD,
                               query_url,
                               headers,
                               query_parameters,
                               None,
                               None)

    def post(self, query_url,
             headers={},
             query_parameters={},
             parameters={},
             files={}):
        """Create a simple POST CoreHttpRequest object for the given parameters

        Args:
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.
            parameters (dict, optional): Form or body parameters to be included
                in the body.
            files (dict, optional): Files to be sent with the request.

        Returns:
            CoreHttpRequest: The generated CoreHttpRequest for the given paremeters.

        """
        return CoreHttpRequest(CoreHttpMethodEnum.POST,
                               query_url,
                               headers,
                               query_parameters,
                               parameters,
                               files)

    def put(self, query_url,
            headers={},
            query_parameters={},
            parameters={},
            files={}):
        """Create a simple PUT CoreHttpRequest object for the given parameters

        Args:
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.
            parameters (dict, optional): Form or body parameters to be included
                in the body.
            files (dict, optional): Files to be sent with the request.

        Returns:
            CoreHttpRequest: The generated CoreHttpRequest for the given paremeters.

        """
        return CoreHttpRequest(CoreHttpMethodEnum.PUT,
                               query_url,
                               headers,
                               query_parameters,
                               parameters,
                               files)

    def patch(self, query_url,
              headers={},
              query_parameters={},
              parameters={},
              files={}):
        """Create a simple PATCH CoreHttpRequest object for the given parameters

        Args:
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.
            parameters (dict, optional): Form or body parameters to be included
                in the body.
            files (dict, optional): Files to be sent with the request.

        Returns:
            CoreHttpRequest: The generated CoreHttpRequest for the given paremeters.

        """
        return CoreHttpRequest(CoreHttpMethodEnum.PATCH,
                               query_url,
                               headers,
                               query_parameters,
                               parameters,
                               files)

    def delete(self, query_url,
               headers={},
               query_parameters={},
               parameters={},
               files={}):
        """Create a simple DELETE CoreHttpRequest object for the given parameters

        Args:
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.
            parameters (dict, optional): Form or body parameters to be
                included in the body.
            files (dict, optional): Files to be sent with the request.

        Returns:
            CoreHttpRequest: The generated CoreHttpRequest for the given paremeters.

        """
        return CoreHttpRequest(CoreHttpMethodEnum.DELETE,
                               query_url,
                               headers,
                               query_parameters,
                               parameters,
                               files)
