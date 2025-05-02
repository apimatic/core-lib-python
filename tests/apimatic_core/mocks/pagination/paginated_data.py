class PaginatedData:
    def __init__(self, request_builder=None, response_body=None, response_headers=None, last_data_size=None):
        self._request_builder = request_builder
        self._response_body = response_body
        self._response_headers = response_headers
        self._last_data_size = last_data_size

    def get_last_response(self):
        return self._response_body

    def get_last_request_builder(self):
        return self._request_builder

    def get_last_response_headers(self):
        return self._response_headers

    def get_last_data_size(self):
        return self._last_data_size
