from collections.abc import Iterator

class PaginatedData(Iterator):
    def __init__(self, api_call, initial_data, *data_managers):
        self.api_call = api_call
        self.data_managers = data_managers

        self.current_index = 0
        self.data = initial_data if initial_data else []
        self.pages = [initial_data] if initial_data else []
        self.last_data_size = len(initial_data) if initial_data else 0
        self.last_response = api_call.last_response

    def get_last_request_builder(self):
        return self.api_call.request_builder

    def get_last_response(self):
        return self.last_response.text

    def get_last_response_headers(self):
        return self.last_response.headers

    def get_last_data_size(self):
        return self.last_data_size

    def reset(self):
        if self.current_index == 0:
            return self
        new_instance = PaginatedData(self.api_call, self.data.copy(), *self.data_managers)
        new_instance.pages = self.pages.copy()
        new_instance.last_data_size = self.last_data_size
        return new_instance

    def __iter__(self):
        return self.reset()

    def __next__(self):
        if self.has_next():
            item = self.data[self.current_index]
            self.current_index += 1
            return item
        raise StopIteration("No more data available.")

    def has_next(self):
        if self.current_index < len(self.data):
            return True
        self.fetch_more_data()
        return self.current_index < len(self.data)

    def pages_iter(self):
        data = self.reset()
        current_index = 0

        def generator():
            nonlocal current_index
            while True:
                if current_index < len(data.pages):
                    yield data.pages[current_index]
                    current_index += 1
                elif data.has_next():
                    next(data)
                else:
                    break

        return generator()

    def convert(self, return_type_getter):
        return return_type_getter(self)

    def fetch_more_data(self):
        from apimatic_core.api_call import ApiCall
        from apimatic_core.response_handler import ResponseHandler
        from apimatic_core.request_builder import RequestBuilder

        for manager in self.data_managers:
            if not manager.is_valid(self, ):
                continue
            try:
                result = ApiCall(self.api_call.global_config).new_builder \
                    .request(RequestBuilder().clone_with(self.api_call.request_builder)) \
                    .response(ResponseHandler().clone_with(self.api_call.response_handler)) \
                    .endpoint_configuration(self.api_call.endpoint_config) \
                    .execute()

                new_data = result
                self.data.extend(new_data)
                self.pages.append(new_data)
                self.last_data_size = len(new_data)
                self.last_response = result.last_response
                return
            except Exception:
                pass
