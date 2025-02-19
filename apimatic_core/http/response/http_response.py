# -*- coding: utf-8 -*-
from apimatic_core.http.request.http_request import HttpRequest
from pydantic import BaseModel
from typing import Dict


class HttpResponse(BaseModel):
    """Information about an HTTP Response including its status code, returned
        headers, and raw body

    Attributes:
        status_code (int): The status code response from the server that
            corresponds to this response.
        reason_phrase (string): The reason phrase returned by the server.
        headers (dict): A dictionary of headers (key : value) that were
            returned with the response
        text (string): The Raw body of the HTTP Response as a string
        request (HttpRequest): The request that resulted in this response.

    """

    status_code: int
    reason_phrase: str
    headers: Dict[str, str]
    text: str
    request: HttpRequest
