from core_interfaces.factories.response_factory import ResponseFactory
from core_lib.http.response.http_response import HttpResponse


class HttpResponseFactory(ResponseFactory):

    def __init__(self):
        pass

    def create(self, status_code, reason, headers, body, request):
        return HttpResponse(status_code, reason, headers, body, request)
