from apimatic_core_interfaces.http.http_response import HttpResponse
from typing import Any, Optional, List

from apimatic_core.http.response.api_response import ApiResponse as CoreApiResponse


class ApiResponse(CoreApiResponse):
    """Http response received.

    Attributes:
        status_code (int): The status code response from the server that
            corresponds to this response.
        reason_phrase (string): The reason phrase returned by the server.
        headers (dict): A dictionary of headers (key : value) that were
            returned with the response
        text (string): The Raw body of the HTTP Response as a string
        request (HttpRequest): The request that resulted in this response.
        body (Object): The data field specified for the response
        errors (Array<String>): Any errors returned by the server

    """

    def __init__(self, http_response: HttpResponse,
                 body: Any = None,
                 errors: Optional[List[str]] = None):
        """The Constructor

        Args:
            http_response (HttpResponse): The original, raw response from the api
            data (Object): The data field specified for the response
            errors (Array<String>): Any errors returned by the server

        """

        super().__init__(http_response, body, errors)

    def __repr__(self):
        return '<Test ApiResponse [%s]>' % self.text

    @staticmethod
    def create(_parent_instance: CoreApiResponse):
        return ApiResponse(
            HttpResponse(
                status_code=_parent_instance.status_code, reason_phrase=_parent_instance.reason_phrase,
                headers=_parent_instance.headers, text=_parent_instance.text, request=_parent_instance.request),
            body=_parent_instance.body, errors=_parent_instance.errors)
