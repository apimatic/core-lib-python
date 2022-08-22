
class RequestBuilder:

    def __init__(
            self,
            server,
            path,
            http_method,
            template_params,
            header_params,
            query_params,
            form_params,
            body_param,
    ):
        self.server = server
        self.path = path
        self.http_method = http_method
        self.template_params = template_params
        self.header_params = header_params
        self.query_params = query_params
        self.form_params = form_params
        self.body_param = body_param

    def build(self):
        pass