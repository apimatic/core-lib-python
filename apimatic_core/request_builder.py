from __future__ import annotations
from typing import Optional, Dict, Any, List, Union, Tuple

from apimatic_core_interfaces.authentication.authentication import Authentication
from apimatic_core_interfaces.http.http_method_enum import HttpMethodEnum
from apimatic_core_interfaces.http.http_request import HttpRequest
from pydantic import validate_call

from apimatic_core.configurations.global_configuration import GlobalConfiguration
from apimatic_core.exceptions.auth_validation_exception import AuthValidationException
from apimatic_core.types.array_serialization_format import SerializationFormats
from apimatic_core.types.file_wrapper import FileType
from apimatic_core.types.parameter import Parameter
from apimatic_core.types.xml_attributes import XmlAttributes
from apimatic_core.utilities.api_helper import ApiHelper


class RequestBuilder:

    def __init__(self):

        self._server: Any = None
        self._path: Optional[str] = None
        self._http_method: Optional[HttpMethodEnum] = None
        self._template_params: Dict[str, Dict[str, Any]] = {}
        self._header_params: Dict[str, Any] = {}
        self._query_params: Dict[str, Any] = {}
        self._form_params: Dict[str, Any] = {}
        self._additional_form_params: Dict[str, Any] = {}
        self._additional_query_params: Dict[str, Any] = {}
        self._multipart_params: List[Parameter] = []
        self._body_param: Any = None
        self._body_serializer: Any = None
        self._auth: Optional[Authentication] = None
        self._array_serialization_format: SerializationFormats = SerializationFormats.INDEXED
        self._xml_attributes: Optional[XmlAttributes] = None

    @validate_call
    def server(self, server: Any) -> 'RequestBuilder':
        self._server = server
        return self

    @validate_call
    def path(self, path: str) -> 'RequestBuilder':
        self._path = path
        return self

    @validate_call
    def http_method(self, http_method: HttpMethodEnum) -> 'RequestBuilder':
        self._http_method = http_method
        return self

    @validate_call
    def template_param(self, template_param: Parameter) -> 'RequestBuilder':
        if template_param.is_valid_parameter() and template_param.key is not None:
            self._template_params[template_param.key] = {
                'value': template_param.value, 'encode': template_param.should_encode
            }
        return self

    @validate_call
    def header_param(self, header_param: Parameter) -> 'RequestBuilder':
        if header_param.is_valid_parameter() and header_param.key is not None:
            self._header_params[header_param.key] = header_param.value
        return self

    @validate_call
    def query_param(self, query_param: Parameter) -> 'RequestBuilder':
        if query_param.is_valid_parameter() and query_param.key is not None:
            self._query_params[query_param.key] = query_param.value
        return self

    @validate_call
    def form_param(self, form_param: Parameter) -> 'RequestBuilder':
        if form_param.is_valid_parameter() and form_param.key is not None:
            self._form_params[form_param.key] = form_param.value
        return self

    @validate_call
    def additional_form_params(self, additional_form_params: Dict[str, Any]) -> 'RequestBuilder':
        self._additional_form_params = additional_form_params
        return self

    @validate_call
    def additional_query_params(self, additional_query_params: Dict[str, Any]) -> 'RequestBuilder':
        self._additional_query_params = additional_query_params
        return self

    @validate_call
    def multipart_param(self, multipart_param: Parameter) -> 'RequestBuilder':
        if multipart_param.is_valid_parameter():
            self._multipart_params.append(multipart_param)
        return self

    @validate_call
    def body_param(self, body_param: Parameter):
        if body_param.is_valid_parameter():
            if body_param.key is not None:
                if not self._body_param:
                    self._body_param = dict()
                self._body_param[body_param.key] = body_param.value
            else:
                self._body_param = body_param.value
        return self

    @validate_call
    def body_serializer(self, body_serializer: Any) -> 'RequestBuilder':
        self._body_serializer = body_serializer
        return self

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def auth(self, auth: Authentication) -> 'RequestBuilder':
        self._auth = auth
        return self

    @validate_call
    def array_serialization_format(self, array_serialization_format: SerializationFormats) -> 'RequestBuilder':
        self._array_serialization_format = array_serialization_format
        return self

    @validate_call
    def xml_attributes(self, xml_attributes: XmlAttributes) -> 'RequestBuilder':
        self._xml_attributes = xml_attributes
        return self

    @validate_call
    def build(self, global_configuration: GlobalConfiguration) -> HttpRequest:
        _url: str = self.process_url(global_configuration)

        _request_headers: Dict[str, Any] = self.process_request_headers(global_configuration)

        _request_body: Any = self.process_body_params()

        _multipart_params: Dict[str, Any] = self.process_multipart_params()

        http_request: HttpRequest = HttpRequest(
            http_method=self._http_method, query_url=_url, headers=_request_headers,
            parameters=_request_body, files=_multipart_params)

        self.apply_auth(global_configuration.auth_managers, http_request)

        return http_request

    @validate_call
    def process_url(self, global_configuration: GlobalConfiguration) -> str:
        _url: str = global_configuration.get_base_uri(self._server) or ''
        if self._template_params:
            _url += ApiHelper.append_url_with_template_parameters(
                self._path, self._template_params)
        elif self._path is not None:
            _url += self._path
        _url = self.get_updated_url_with_query_params(_url)
        return ApiHelper.clean_url(_url)

    @validate_call
    def get_updated_url_with_query_params(self, _query_builder: str) -> str:
        if self._additional_query_params:
            self.add_additional_query_params()
        return ApiHelper.append_url_with_query_parameters(
            _query_builder, self._query_params, self._array_serialization_format)\
            if self._query_params else _query_builder

    @validate_call
    def process_request_headers(self, global_configuration: GlobalConfiguration) -> Dict[str, Any]:
        request_headers: Dict[str, Any] = self._header_params
        global_headers: Dict[str, Any] = global_configuration.global_headers
        additional_headers: Dict[str, Any] = global_configuration.additional_headers

        if global_headers:
            prepared_headers: Dict[str, Any] = {key: str(value) if value is not None else value
                                for key, value in self._header_params.items()}
            request_headers = {**global_headers, **prepared_headers}

        if additional_headers:
            request_headers.update(additional_headers)

        return request_headers

    @validate_call
    def process_body_params(
            self
    ) -> Union[None, List[Tuple[str, Any]], Dict[str, Any], Union[FileType, Parameter], str]:
        if self._xml_attributes:
            return self.process_xml_parameters(self._body_serializer)
        elif self._form_params or self._additional_form_params:
            self.add_additional_form_params()
            return ApiHelper.form_encode_parameters(self._form_params, self._array_serialization_format)
        elif self._body_param is not None and self._body_serializer:
            return self._body_serializer(self.resolve_body_param())
        elif self._body_param is not None and not self._body_serializer:
            return self.resolve_body_param()

        return None

    @validate_call
    def process_xml_parameters(self, body_serializer: Any) -> str:
        if self._xml_attributes is None:
            raise ValueError('XML attributes are not set')

        if self._xml_attributes.array_item_name:
            return body_serializer(self._xml_attributes.value,
                                   self._xml_attributes.root_element_name,
                                   self._xml_attributes.array_item_name)

        return body_serializer(self._xml_attributes.value, self._xml_attributes.root_element_name)

    @validate_call
    def add_additional_form_params(self):
        if self._additional_form_params:
            for form_param in self._additional_form_params:
                self._form_params[form_param] = self._additional_form_params[form_param]

    @validate_call
    def add_additional_query_params(self):
        for query_param in self._additional_query_params:
            self._query_params[query_param] = self._additional_query_params[query_param]

    @validate_call
    def resolve_body_param(self) -> Union[FileType, Parameter]:
        if ApiHelper.is_file_wrapper_instance(self._body_param):
            if self._body_param.content_type:
                self._header_params['content-type'] = self._body_param.content_type
            return self._body_param.file_stream

        return self._body_param

    @validate_call
    def process_multipart_params(self) -> Dict[str, Union[Tuple[Optional[str], FileType, Optional[str]]]]:
        multipart_params: Dict[str, Union[Tuple[Optional[str], FileType, Optional[str]]]] = {}
        for multipart_param in self._multipart_params:
            if multipart_param.key is None:
                continue

            param_value = multipart_param.value
            if ApiHelper.is_file_wrapper_instance(param_value):
                file: FileType = param_value.file_stream # TextIO, BinaryIO, BufferedIOBase, TextIOWrapper
                multipart_params[multipart_param.key] = (file.name if hasattr(file, "name") else None,
                                                         file, param_value.content_type)
            else:
                param_name = param_value.name if not isinstance(param_value, str) else None
                multipart_params[multipart_param.key] = (
                    param_name, param_value, multipart_param.default_content_type
                )

        return multipart_params

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def apply_auth(self, auth_managers: Dict[str, Authentication], http_request: HttpRequest):
        if self._auth:
            if self._auth.with_auth_managers(auth_managers).is_valid():
                self._auth.apply(http_request)
            else:
                raise AuthValidationException(self._auth.error_message)
