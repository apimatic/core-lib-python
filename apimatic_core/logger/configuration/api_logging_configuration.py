from apimatic_core_interfaces.logger.logger import Logger


class ApiLoggingConfiguration:

    @property
    def logger(self):
        return self._logger

    @property
    def log_level(self):
        return self._log_level

    @property
    def mask_sensitive_headers(self):
        return self._mask_sensitive_headers

    @property
    def request_logging_config(self):
        return self._request_logging_config

    @property
    def response_logging_config(self):
        return self._response_logging_config

    def __init__(self, logger, log_level, mask_sensitive_headers,
                 request_logging_config, response_logging_config):
        """Default constructor.

        Args:
            logger (Logger): The logger implementation to log with.
            log_level (LogLevel): The log level to apply to the log message.
            mask_sensitive_headers (bool): Flag to control masking of sensitive headers.
            request_logging_config (ApiRequestLoggingConfiguration): The API request logging configuration.
            response_logging_config (ApiResponseLoggingConfiguration): The API response logging configuration.
        """

        self._logger = logger
        self._log_level = log_level
        self._mask_sensitive_headers = mask_sensitive_headers
        self._request_logging_config = request_logging_config
        self._response_logging_config = response_logging_config


class BaseLoggingConfiguration:

    @property
    def log_body(self):
        return self._log_body

    @property
    def log_headers(self):
        return self._log_headers

    @property
    def headers_to_include(self):
        return self._headers_to_include

    @property
    def headers_to_exclude(self):
        return self._headers_to_exclude

    @property
    def headers_to_unmask(self):
        return self._headers_to_unmask

    def __init__(self, log_body, log_headers, headers_to_include,
                 headers_to_exclude, headers_to_unmask):
        """Default constructor.

        Args:
            log_body (bool): Controls the logging of the request body.
            log_headers (bool): Controls the logging of request headers.
            headers_to_include (List[str]): Includes only specified headers in the log output.
            headers_to_exclude (List[str]): Excludes specified headers from the log output.
            headers_to_unmask (List[str]): Logs specified headers without masking, revealing their actual values.
        """

        self._log_body = log_body
        self._log_headers = log_headers
        self._headers_to_include = [] if headers_to_include is None \
            else list(map(lambda x: x.lower(), headers_to_include))
        self._headers_to_exclude = [] if headers_to_exclude is None \
            else list(map(lambda x: x.lower(), headers_to_exclude))
        self._headers_to_unmask = [] if headers_to_unmask is None \
            else list(map(lambda x: x.lower(), headers_to_unmask))


class ApiRequestLoggingConfiguration(BaseLoggingConfiguration):

    @property
    def include_query_in_path(self):
        return self._include_query_in_path

    def __init__(self, log_body, log_headers, headers_to_include,
                 headers_to_exclude, headers_to_unmask,
                 include_query_in_path):
        """Default constructor.

        Args:
            log_body (bool): Controls the logging of the request body.
            log_headers (bool): Controls the logging of request headers.
            headers_to_include (List[str]): Includes only specified headers in the log output.
            headers_to_exclude (List[str]): Excludes specified headers from the log output.
            headers_to_unmask (List[str]): Logs specified headers without masking, revealing their actual values.
            include_query_in_path (bool): Determines whether to include query parameters in the logged request path.
        """
        super(ApiRequestLoggingConfiguration, self).__init__(log_body, log_headers, headers_to_include,
                                                             headers_to_exclude, headers_to_unmask)
        self._include_query_in_path = include_query_in_path


class ApiResponseLoggingConfiguration(BaseLoggingConfiguration):

    def __init__(self, log_body, log_headers, headers_to_include,
                 headers_to_exclude, headers_to_unmask):
        """Default constructor.

        Args:
            log_body (bool): Controls the logging of the request body.
            log_headers (bool): Controls the logging of request headers.
            headers_to_include (List[str]): Includes only specified headers in the log output.
            headers_to_exclude (List[str]): Excludes specified headers from the log output.
            headers_to_unmask (List[str]): Logs specified headers without masking, revealing their actual values.
        """

        super(ApiResponseLoggingConfiguration, self).__init__(log_body, log_headers, headers_to_include,
                                                              headers_to_exclude, headers_to_unmask)