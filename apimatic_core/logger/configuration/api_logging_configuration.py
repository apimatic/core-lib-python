import logging

from apimatic_core_interfaces.logger.logger import Logger
from pydantic import validate_call, BaseModel, field_validator, Field
from typing import List, Dict, Any

from apimatic_core.constants.logger_constants import LoggerConstants
from apimatic_core.logger.default_logger import ConsoleLogger
from apimatic_core.utilities.api_helper import ApiHelper

class BaseHttpLoggingConfiguration(BaseModel):
    log_body: bool
    log_headers: bool
    headers_to_include: List[str] = Field(default_factory=list)
    headers_to_exclude: List[str] = Field(default_factory=list)
    headers_to_unmask: List[str] = Field(default_factory=list)

    @field_validator("headers_to_include", "headers_to_exclude", "headers_to_unmask", mode="before")
    def to_lower_case_list(cls, value):
        return ApiHelper.to_lower_case(value) if value else []

    @validate_call
    def get_loggable_headers(self, headers: Dict[str, Any], mask_sensitive_headers: bool) -> Dict[str, Any]:
        """
        Retrieves the headers to be logged based on the provided logging configuration,
        headers, and sensitivity masking configuration.

        Args:
            headers (Dict[str, str]): The headers to be evaluated for logging.
            mask_sensitive_headers (bool): Determines whether sensitive headers should be
                                            masked in the log.

        Returns:
            Dict[str, str]: A map containing the headers to be logged, considering the provided
                            configuration and sensitivity masking.
        """
        extracted_headers = self._extract_headers_to_log(headers)

        return self._mask_sensitive_headers(extracted_headers, mask_sensitive_headers)

    @validate_call
    def _extract_headers_to_log(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts headers to log based on inclusion and exclusion criteria.

        Args:
            headers (Dict[str, str]): The map of headers.

        Returns:
            Dict[str, str]: The extracted headers to log.
        """
        if self.headers_to_include:
            return self._filter_included_headers(headers)
        if self.headers_to_exclude:
            return self._filter_excluded_headers(headers)

        return headers

    @validate_call
    def _mask_sensitive_headers(self, headers: Dict[str, Any], mask_sensitive_headers: bool) -> Dict[str, Any]:
        """
        Masks sensitive headers from the given list of request headers.

        Args:
            headers (Dict[str, str]): The list of headers to filter.
            mask_sensitive_headers (bool): Whether to mask sensitive headers or not.

        Returns:
            Dict[str, str]: A map containing filtered headers.
        """
        if not mask_sensitive_headers:
            return headers

        filtered_headers = {}
        for key, value in headers.items():
            header_key = key.lower()
            is_non_sensitive = (header_key in LoggerConstants.NON_SENSITIVE_HEADERS or
                                header_key in self.headers_to_unmask)
            filtered_headers[key] = value if is_non_sensitive else "**Redacted**"

        return filtered_headers

    @validate_call
    def _filter_included_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters headers to log based on inclusion criteria.

        Args:
            headers (Dict[str, str]): The map of headers.

        Returns:
            Dict[str, str]: The extracted headers to log.
        """
        extracted_headers = {}
        for key, value in headers.items():
            if key.lower() in self.headers_to_include:
                extracted_headers[key] = value
        return extracted_headers

    def _filter_excluded_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters headers to log based on exclusion criteria.

        Args:
            headers (Dict[str, str]): The map of headers.

        Returns:
            Dict[str, str]: The extracted headers to log.
        """
        extracted_headers = {}
        for key, value in headers.items():
            if key.lower() not in self.headers_to_exclude:
                extracted_headers[key] = value
        return extracted_headers

class ApiRequestLoggingConfiguration(BaseHttpLoggingConfiguration):
    include_query_in_path: bool

    @validate_call
    def get_loggable_url(self, query_url: str) -> str:
        """
        Retrieves a URL suitable for logging purposes.

        This method determines the URL to be logged based on the `include_query_in_path` configuration.

        Args:
            query_url (str): The original URL containing query parameters.

        Returns:
            str: The URL to be logged.
                - If `include_query_in_path` is True, the original URL with query parameters is returned.
                - If `include_query_in_path` is False (default), the URL without query parameters is returned.
        """
        if self.include_query_in_path:
            return query_url

        return ApiHelper.get_url_without_query(query_url)


class ApiResponseLoggingConfiguration(BaseHttpLoggingConfiguration):
    pass

class ApiLoggingConfiguration(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    logger: Logger = ConsoleLogger()
    log_level: int = logging.INFO
    mask_sensitive_headers: bool
    request_logging_config: ApiRequestLoggingConfiguration
    response_logging_config: ApiResponseLoggingConfiguration
