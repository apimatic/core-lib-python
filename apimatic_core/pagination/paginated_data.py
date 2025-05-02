from apimatic_core.utilities.api_helper import ApiHelper
from collections.abc import Iterator

class PaginatedData(Iterator):
    def __init__(self, page_class, converter, response, endpoint_config, global_config, *data_managers):
        self.page_class = page_class
        self.converter = converter
        self.data_managers = data_managers

        self.current_index = 0
        self.data = []
        self.pages = []
        self.last_data_size = 0
        self.last_response = None
        self.last_endpoint_config = None
        self.last_global_config = None

        self.update_using(response, endpoint_config, global_config)

    def update_using(self, response, endpoint_config, global_config):
        page = ApiHelper.json_deserialize(response.text, self.page_class.from_dictionary)
        new_data = self.converter(page)

        self.last_data_size = len(new_data)
        self.last_response = response
        self.last_endpoint_config = endpoint_config
        self.last_global_config = global_config

        self.data.extend(new_data)
        self.pages.append(page)

    def get_last_request_builder(self):
        return self.last_endpoint_config.request_builder

    def get_last_response(self):
        return self.last_response.text

    def get_last_response_headers(self):
        return self.last_response.headers

    def get_last_data_size(self):
        return self.last_data_size

    def reset(self):
        if self.current_index == 0:
            return self
        new_instance = PaginatedData(
            self.page_class, self.converter, self.last_response, self.last_endpoint_config, self.last_global_config, *self.data_managers
        )
        new_instance.data = list(self.data)
        new_instance.pages = list(self.pages)
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
                    data.__next__()
                else:
                    break

        return generator()

    def convert(self, return_type_getter):
        return return_type_getter(self)

    def fetch_more_data(self):
        from apimatic_core.api_call import ApiCall
        from apimatic_core.response_handler import ResponseHandler

        for manager in self.data_managers:
            if not manager.is_valid(self):
                continue
            try:
                endpoint_config = self.last_endpoint_config
                global_config = self.last_global_config

                result = ApiCall(global_config).new_builder \
                    .request(
                        manager.get_next_request_builder(self)
                     ) \
                    .response(ResponseHandler()
                              .paginated_deserializer(
                                  self.page_class,
                                  self.converter,
                                  lambda r :r,
                     self.data_managers)) \
                    .endpoint_configuration(endpoint_config) \
                    .execute()


                self.update_using(result.last_response, result.last_endpoint_config, result.last_global_config)
                return
            except Exception:
                pass

