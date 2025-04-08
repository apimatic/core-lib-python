from jsonpointer import resolve_pointer
from apimatic_core.utilities.api_helper import ApiHelper


class PaginatedData:
    """Base class for paginated data, implementing Python's iterator protocol."""

    def __init__(self, value, response, config, result_pointer):
        self.current_index = 0
        self.data = [value]  # Stores fetched items
        self.responses = [response]  # Stores API responses
        self.endpoint_configs = [config]  # Stores endpoint configurations
        self.result_pointer = result_pointer

    def __iter__(self):
        return self  # Return self to make this an iterator

    def __next__(self):
        if self.has_next():
            value = self.data[self.current_index]
            self.current_index += 1
            return value
        raise StopIteration("No more data available.")

    def has_next(self):
        """Checks if there is more data available."""
        if self.current_index < len(self.data):
            return True

        next_data = self.fetch_data()
        if next_data:
            self.update_using(next_data)
            return True

        return False

    def update_using(self, existing):
        """Updates pagination state with newly fetched data."""
        self.data.append(existing.data[existing.current_index])
        self.responses.append(existing.responses[existing.current_index])
        self.endpoint_configs.append(existing.endpoint_configs[existing.current_index])

    def get_last_endpoint_configuration(self):
        return self.endpoint_configs[self.current_index - 1]

    def get_last_response(self):
        return self.responses[self.current_index - 1]

    def __str__(self):
        return f"PaginatedData [current_index={self.current_index}, data={self.data}]"

    def fetch_data(self):
        """Abstract method that should be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement fetch_data()")

class OffsetPaginated(PaginatedData):
    """Offset-based pagination, extends PaginatedData."""

    def __init__(self, deserializer, deserialize_into, configuration, endpoint_config, response):
        super().__init__(deserializer(response.text, deserialize_into), response, endpoint_config, configuration.result_pointer)
        self.deserializer = deserializer
        self.deserialize_into = deserialize_into
        self.configuration = configuration

    @staticmethod
    def create(deserializer, deserialize_into,  configuration, endpoint_config, response):
        return OffsetPaginated(deserializer, deserialize_into, configuration, endpoint_config, response)

    def fetch_data(self):
        """Fetches the next page of data."""
        from apimatic_core.api_call import ApiCall
        endpoint_config = self.get_last_endpoint_configuration()
        try:
            return (ApiCall(endpoint_config.get_global_configuration()).new_builder.
                      request(self.configuration.get_next_page_request(
                        endpoint_config.get_request_builder(),
                        endpoint_config.get_global_configuration(),
                        self.get_last_response().text)
                      )
                      .response(lambda res: res.offset_paginated_deserializer(
                        self.deserializer, self.deserialize_into, self.configuration)
                      )
                      .endpoint_configuration(endpoint_config)
                    ).execute()
        except Exception:
            return None

class CursorPaginated(PaginatedData):
    """Cursor-based pagination, extends PaginatedData."""

    def __init__(self, deserializer, deserialize_into, configuration, endpoint_config, response):
        super().__init__(deserializer(response.text, deserialize_into), response, endpoint_config, configuration.result_pointer)
        self.deserializer = deserializer
        self.configuration = configuration
        self.deserialize_into = deserialize_into

    @staticmethod
    def create(deserializer, deserialize_into, configuration, endpoint_config, response):
        return CursorPaginated(deserializer, deserialize_into, configuration, endpoint_config, response)

    def fetch_data(self):
        """Fetches the next page of data using cursor-based pagination."""
        from apimatic_core.api_call import ApiCall

        cursor_value = ApiHelper.json_deserialize(resolve_pointer(self.get_last_response().text, self.configuration.next_cursor))
        endpoint_config = self.get_last_endpoint_configuration()

        if cursor_value is None:
            return None

        try:
            return (ApiCall(endpoint_config.get_global_configuration()).new_builder()
                    .request(self.configuration.get_next_page_request(
                        endpoint_config.get_request_builder(),
                        endpoint_config.get_global_configuration(),
                        self.get_last_response().text)
                    )
                    .response(lambda res: res.cursor_paginated_deserializer(self.deserializer, self.deserialize_into, self.configuration))
                    .endpoint_configuration(endpoint_config)
                    ).execute()
        except Exception:
            return None

class LinkPaginated(PaginatedData):
    """Link-based pagination, extends PaginatedData."""

    def __init__(self, deserializer, deserialize_into, configuration, endpoint_config, response):
        super().__init__(deserializer(response.text, deserialize_into), response, endpoint_config, configuration.result_pointer)
        self.deserializer = deserializer
        self.configuration = configuration
        self.deserialize_into = deserialize_into

    @staticmethod
    def create(deserializer, deserialize_into, configuration, endpoint_config, response):
        return LinkPaginated(deserializer, deserialize_into, configuration, endpoint_config, response)

    def fetch_data(self):
        """Fetches the next page of data using link-based pagination."""
        from apimatic_core.api_call import ApiCall
        link_value = ApiHelper.json_deserialize(resolve_pointer(self.get_last_response().text, self.configuration.next_pointer))
        endpoint_config = self.get_last_endpoint_configuration()

        if link_value is None:
            return None

        try:
            return (ApiCall(endpoint_config.get_global_configuration()).new_builder()
                    .request(self.configuration.get_next_page_request(
                        endpoint_config.get_request_builder(),
                        endpoint_config.get_global_configuration(),
                        link_value)
                    )
                    .response(lambda res: res.link_paginated_deserializer(self.deserializer, self.deserialize_into, self.configuration))
                    .endpoint_configuration(endpoint_config)
                    ).execute()
        except Exception:
            return None

