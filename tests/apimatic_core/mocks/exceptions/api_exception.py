from apimatic_core_interfaces.http.http_response import HttpResponse
from pydantic import BaseModel


class APIExceptionValidator(BaseModel):
    reason: str
    response: HttpResponse

class APIException(Exception):

    """Class that handles HTTP Exceptions when fetching API Endpoints.

    Attributes:
        response_code (int): The status code of the response.
        response (HttpResponse): The HttpResponse of the API call.

    """

    reason: str
    response: HttpResponse
    response_code: int

    def __init__(self,
                 reason: str,
                 response: HttpResponse):
        """Constructor for the APIException class

        Args:
            reason (string): The reason (or error message) for the Exception
                to be raised.
            response (HttpResponse): The HttpResponse of the API call.

        """

        APIExceptionValidator(reason=reason, response=response)
        super(APIException, self).__init__(reason)
        self.reason = reason
        self.response = response
        self.response_code = response.status_code
