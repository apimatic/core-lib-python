from apimatic_core_interfaces.http.http_request import HttpRequest
from apimatic_core_interfaces.http.http_response import HttpResponse
from typing import Optional, List, Any, Dict

from pydantic import BaseModel


class ApiResponse(BaseModel):

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
    status_code: int
    reason_phrase: Optional[str]
    headers: Dict[str, str]
    text: Any
    request: HttpRequest
    body: Any
    errors: Optional[List[str]]

    def __init__(self, http_response: HttpResponse,
                 body: Any=None,
                 errors: Optional[List[str]]=None):

        """The Constructor

        Args:
            http_response (HttpResponse): The original, raw response from the api
            body (Any): The response body
            errors (Array<String>): Any errors returned by the server

        """
        super().__init__(status_code=http_response.status_code,
                         reason_phrase=http_response.reason_phrase,
                         headers=http_response.headers,
                         text=http_response.text,
                         request=http_response.request,
                         body=body,
                         errors=errors)

    def is_success(self) -> bool:
        """ Returns true if status code is between 200-300

        """
        return 200 <= self.status_code < 300

    def is_error(self) -> bool:
        """ Returns true if status code is between 400-600

        """
        return 400 <= self.status_code < 600

    def __repr__(self) -> str:
        return '<CoreApiResponse {}>'.format(self.text)
