from core_lib.http.request.http_request import HttpRequest
from core_lib.utilities.api_helper import ApiHelper


class RequestBuilder:

    def __init__(
            self
    ):
        self._server = None
        self._path = None
        self._http_method = None
        self._template_params = {}
        self._header_params = {}
        self._query_params = {}
        self._form_params = {}
        self._additional_form_params = {}
        self._multipart_params = []
        self._body_param = None
        self._body_serializer = None
        self._auth = None

    def server(self, server):
        self._server = server
        return self

    def path(self, path):
        self._path = path
        return self

    def http_method(self, http_method):
        self._http_method = http_method
        return self

    def template_param(self, template_param):
        template_param.validate()
        self._template_params[template_param.get_key()] = {'value': template_param.get_value(),
                                                           'encode': template_param.need_to_encode()}
        return self

    def header_param(self, header_param):
        header_param.validate()
        self._header_params[header_param.get_key()] = header_param.get_value()
        return self

    def query_param(self, query_param):
        query_param.validate()
        self._query_params[query_param.get_key()] = query_param.get_value()
        return self

    def form_param(self, form_param):
        form_param.validate()
        self._form_params[form_param.get_key()] = form_param.get_value()
        return self

    def additional_form_params(self, additional_form_params):
        self._additional_form_params = additional_form_params
        return self

    def multipart_param(self, multipart_param):
        multipart_param.validate()
        self._multipart_params.append(multipart_param)
        return self

    def body_param(self, body_param):
        body_param.validate()
        self._body_param = body_param.get_value()
        return self

    def body_serializer(self, body_serializer):
        self._body_serializer = body_serializer
        return self

    def auth(self, auth):
        self._auth = auth
        return self

    def build(self, global_configuration):
        _url = self.process_url(global_configuration)

        _request_headers = self.process_request_headers(global_configuration)

        _request_body = self.process_body_params()

        _multipart_params = self.process_multipart_params()

        http_request = HttpRequest(http_method=self._http_method,
                                   query_url=_url,
                                   headers=_request_headers,
                                   parameters=_request_body,
                                   files=_multipart_params)

        self.apply_auth(global_configuration.get_auth_managers(), http_request)

        return http_request

    def process_url(self, global_configuration):
        _url = global_configuration.get_base_uri(self._server)
        _updated_url_with_template_params = self.get_updated_url_with_template_params()
        _url += _updated_url_with_template_params if _updated_url_with_template_params else self._path
        _url = self.get_updated_url_with_query_params(_url)
        return ApiHelper.clean_url(_url)

    def get_updated_url_with_template_params(self):
        return ApiHelper.append_url_with_template_parameters(self._path,
                                                             self._template_params) if self._template_params else None

    def get_updated_url_with_query_params(self, _query_builder):
        return ApiHelper.append_url_with_query_parameters(_query_builder,
                                                          self._query_params) if self._query_params else _query_builder

    def process_request_headers(self, global_configuration):
        global_headers = global_configuration.get_global_headers()
        if global_headers:
            prepared_headers = {key: str(value) for key, value in self._header_params.items()}
            return {**global_headers, **prepared_headers}
        return self._header_params

    def process_body_params(self):
        if self._form_params:
            self.add_additional_form_params()
            return ApiHelper.form_encode_parameters(self._form_params)
        elif self._body_param and self._body_serializer:
            return self._body_serializer(self.resolve_body_param())
        elif self._body_param and not self._body_serializer:
            return self.resolve_body_param()

    def add_additional_form_params(self):
        if self._additional_form_params:
            for form_param in self._additional_form_params:
                self._form_params[form_param] = self._additional_form_params[form_param]

    def resolve_body_param(self):
        if ApiHelper.is_file_wrapper_instance(self._body_param):
            if self._body_param.content_type:
                self._header_params['content-type'] = self._body_param.content_type
            return self._body_param.file_stream

        return self._body_param

    def process_multipart_params(self):
        multipart_params = {}
        for multipart_param in self._multipart_params:
            param_value = multipart_param.get_value()
            if ApiHelper.is_file_wrapper_instance(param_value):
                multipart_params[multipart_param.get_key()] = (
                    param_value.name, param_value.file_stream, param_value.content_type)
            else:
                multipart_params[multipart_param.get_key()] = (self.get_param_name(param_value), param_value,
                                                               multipart_param.get_default_content_type())
        return multipart_params

    def apply_auth(self, auth_managers, http_request):
        if self._auth:
            if self._auth.with_auth_managers(auth_managers).is_valid():
                self._auth.apply(http_request)
            else:
                raise PermissionError(self._auth.error_message)

    @staticmethod
    def get_param_name(param_value):
        if isinstance(param_value, str):
            return None
        return param_value.name
