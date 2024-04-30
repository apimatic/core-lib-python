import logging

from apimatic_core_interfaces.logger.api_logger import ApiLogger

from apimatic_core.constants.logger_constants import LoggerConstants
from apimatic_core.logger.configuration.api_logging_configuration import ApiLoggingConfiguration
from apimatic_core.utilities.api_helper import ApiHelper
from apimatic_core.utilities.log_helper import LogHelper


class SdkLogger(ApiLogger):

    def __init__(self, api_logging_configuration):
        """Default Constructor.

        Args:
            api_logging_configuration (ApiLoggingConfiguration): The Api logging configuration.
        """
        self._api_logging_config = api_logging_configuration
        self._logger = self._api_logging_config.logger
        self._request_logging_config = self._api_logging_config.request_logging_config
        self._response_logging_config = self._api_logging_config.response_logging_config

    def log_request(self, http_request):
        """Logs the given HTTP request.

        Args:
            http_request (HttpRequest): The HTTP request to log.
        """
        _level = logging.INFO if self._api_logging_config.log_level is None else self._api_logging_config.log_level
        _content_type = http_request.headers.get(LoggerConstants.CONTENT_TYPE_HEADER)
        _url = self.get_request_url(http_request)
        params = {
            LoggerConstants.METHOD: http_request.method,
            LoggerConstants.URL: _url,
            LoggerConstants.CONTENT_TYPE: _content_type,
        }

        self._logger.log(_level, f"Request {{{LoggerConstants.METHOD}}} {{{LoggerConstants.URL}}}"
                                 f" {{{LoggerConstants.CONTENT_TYPE}}}", params)

        if self._request_logging_config.log_headers:
            params = {
                LoggerConstants.HEADERS: LogHelper.get_headers_to_log(self._request_logging_config,
                                                                      http_request.headers,
                                                                      self._api_logging_config.mask_sensitive_headers)
            }
            self._logger.log(_level, f"Request Headers {{{LoggerConstants.HEADERS}}}", params)

        if self._request_logging_config.log_body:
            body = http_request.parameters if http_request.parameters is not None else http_request.files
            params = {
                LoggerConstants.BODY: body
            }
            self._logger.log(_level, f"Request Body {{{LoggerConstants.BODY}}}", params)

    def log_response(self, http_response):
        """Logs the given HTTP response.

        Args:
            http_response (HttpRequest): The HTTP request to log.
        """
        _level = logging.INFO if self._api_logging_config.log_level is None else self._api_logging_config.log_level
        _content_type = http_response.headers.get(LoggerConstants.CONTENT_TYPE_HEADER)
        _content_length = http_response.headers.get(LoggerConstants.CONTENT_LENGTH_HEADER)
        params = {
            LoggerConstants.STATUS_CODE: http_response.status_code,
            LoggerConstants.CONTENT_TYPE: _content_type,
            LoggerConstants.CONTENT_LENGTH: _content_length,
        }
        self._logger.log(_level, f"Response {{{LoggerConstants.STATUS_CODE}}} {{{LoggerConstants.CONTENT_TYPE}}}"
                                 f" {{{LoggerConstants.CONTENT_LENGTH}}}", params)

        if self._response_logging_config.log_headers:
            params = {
                LoggerConstants.HEADERS: LogHelper.get_headers_to_log(self._response_logging_config,
                                                                      http_response.headers,
                                                                      self._api_logging_config.mask_sensitive_headers)
            }
            self._logger.log(_level, f"Response Headers {{{LoggerConstants.HEADERS}}}", params)

        if self._response_logging_config.log_body:
            params = {
                LoggerConstants.BODY: http_response.text
            }
            self._logger.log(_level, f"Response Body {{{LoggerConstants.BODY}}}", params)

    def get_request_url(self, http_request):
        if self._request_logging_config.include_query_in_path:
            return http_request.query_url

        return ApiHelper.get_url_without_query(http_request.query_url)


class NoneSdkLogger(ApiLogger):

    def log_request(self, http_request):
        """Logs the given HTTP request.

        Args:
            http_request (HttpRequest): The HTTP request to log.
        """
        pass

    def log_response(self, http_response):
        """Logs the given HTTP response.

        Args:
            http_response (HttpRequest): The HTTP request to log.
        """
        pass


class LoggerFactory:

    @classmethod
    def get_api_logger(cls, api_logging_configuration):
        """Default Constructor.

        Args:
            api_logging_configuration (ApiLoggingConfiguration): The Api logging configuration.

        Returns:
            ApiLogger: The implementation of ApiLogger.
        """
        if api_logging_configuration is None:
            return NoneSdkLogger()

        return SdkLogger(api_logging_configuration)
