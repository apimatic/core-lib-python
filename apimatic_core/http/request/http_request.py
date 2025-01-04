# -*- coding: utf-8 -*-


from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core_interfaces.types.http_method_enum import HttpMethodEnum
from pydantic import BaseModel
from typing import Optional, Dict, List, Any, Tuple


class HttpRequest(BaseModel):
    """Information about an HTTP Request including its method, headers,
        parameters, URL, and Basic Auth details

    Attributes:
        http_method (HttpMethodEnum): The HTTP Method that this request should
            perform when called.
        headers (dict): A dictionary of headers (key : value) that should be
            sent along with the request.
        query_url (string): The URL that the request should be sent to.
        parameters (dict): A dictionary of parameters that are to be sent along
            with the request in the form body of the request

    """

    http_method: str
    query_url: str
    headers: Optional[Dict[str, str]] = None
    query_parameters: Optional[Dict[str, Any]] = None
    parameters: Optional[List[Tuple[str, Any]]] = None
    files: Optional[Dict[str, Any]] = None

    def __init__(self,
                 http_method: str,
                 query_url: str,
                 headers: Optional[Dict[str, str]]=None,
                 query_parameters: Optional[Dict[str, Any]]=None,
                 parameters: Optional[List[Tuple[str, Any]]]=None,
                 files: Optional[Dict[str, Any]]=None) -> None:
        """Constructor for the HttpRequest class

        Args:
            http_method (HttpMethodEnum): The HTTP Method.
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.
            parameters (dict, optional): Form or body parameters to be included
                in the body.
            files (dict, optional): Files to be sent with the request.

        """
        super().__init__(http_method=http_method, query_url=query_url, headers=headers,
                         query_parameters=query_parameters, parameters=parameters, files=files)

    def add_header(self, name: str, value: str) -> None:
        """ Add a header to the HttpRequest.

        Args:
            name (string): The name of the header.
            value (string): The value of the header.

        """
        self.headers[name] = value

    def add_parameter(self, name: str, value: str) -> None:  # pragma: no cover
        """ Add a parameter to the HttpRequest.

        Args:
            name (string): The name of the parameter.
            value (string): The value of the parameter.

        """
        self.parameters[name] = value

    def add_query_parameter(self, name: str, value: str) -> None:
        """ Add a query parameter to the HttpRequest.

        Args:
            name (string): The name of the query parameter.
            value (string): The value of the query parameter.

        """
        self.query_url = ApiHelper.append_url_with_query_parameters(
            self.query_url,
            {name: value}
        )
        self.query_url = ApiHelper.clean_url(self.query_url)

    def __repr__(self) -> str:
        return str(self.__dict__)