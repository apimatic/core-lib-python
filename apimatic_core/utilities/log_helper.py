from apimatic_core.constants.logger_constants import LoggerConstants


class LogHelper:
    NON_SENSITIVE_HEADERS = list(map(lambda x: x.lower(), [
        "Accept", "Accept-Charset", "Accept-Encoding", "Accept-Language",
        "Access-Control-Allow-Origin", "Cache-Control", "Connection",
        "Content-Encoding", "Content-Language", "Content-Length", "Content-Location",
        "Content-MD5", "Content-Range", "Content-Type", "Date", "ETag", "Expect",
        "Expires", "From", "Host", "If-Match", "If-Modified-Since", "If-None-Match",
        "If-Range", "If-Unmodified-Since", "Keep-Alive", "Last-Modified", "Location",
        "Max-Forwards", "Pragma", "Range", "Referer", "Retry-After", "Server",
        "Trailer", "Transfer-Encoding", "Upgrade", "User-Agent", "Vary", "Via",
        "Warning", "X-Forwarded-For", "X-Requested-With", "X-Powered-By"
    ]))
    """List of sensitive headers that need to be filtered."""

    @staticmethod
    def get_headers_to_log(logging_configuration, headers, mask_sensitive_headers):
        """
        Retrieves the headers to be logged based on the provided logging configuration,
        headers, and sensitivity masking configuration.

        Args:
            logging_configuration (BaseLoggingConfiguration): The logging configuration containing configurations for
                                                              header logging for request or response.
            headers (Dict[str, str]): The headers to be evaluated for logging.
            mask_sensitive_headers (bool): Determines whether sensitive headers should be
                                            masked in the log.

        Returns:
            Dict[str, str]: A map containing the headers to be logged, considering the provided
                            configuration and sensitivity masking.
        """
        extracted_headers = LogHelper.extract_headers_to_log(headers,
                                                             logging_configuration.headers_to_include,
                                                             logging_configuration.headers_to_exclude)

        return LogHelper.mask_sensitive_headers(extracted_headers,
                                                logging_configuration.headers_to_unmask,
                                                mask_sensitive_headers)

    @staticmethod
    def extract_headers_to_log(headers, headers_to_include, headers_to_exclude):
        """
        Extracts headers to log based on inclusion and exclusion criteria.

        Args:
            headers (Dict[str, str]): The map of headers.
            headers_to_include (List[str]): The set of headers to include.
            headers_to_exclude (List[str]): The set of headers to exclude.

        Returns:
            Dict[str, str]: The extracted headers to log.
        """
        if headers_to_include:
            return LogHelper.filter_included_headers(headers, headers_to_include)
        if headers_to_exclude:
            return LogHelper.filter_excluded_headers(headers, headers_to_exclude)

        return headers

    @staticmethod
    def mask_sensitive_headers(headers, headers_to_unmask, mask_sensitive_headers):
        """
        Masks sensitive headers from the given list of request headers.

        Args:
            headers (Dict[str, str]): The list of headers to filter.
            headers_to_unmask (List[str]): The list of headers to unmask.
            mask_sensitive_headers (bool): Whether to mask sensitive headers or not.

        Returns:
            Dict[str, str]: A map containing filtered headers.
        """
        if not mask_sensitive_headers:
            return headers

        filtered_headers = {}
        for key, value in headers.items():
            header_key = key.lower()
            is_non_sensitive = header_key in LogHelper.NON_SENSITIVE_HEADERS or header_key in headers_to_unmask
            filtered_headers[key] = value if is_non_sensitive else "**Redacted**"

        return filtered_headers

    @staticmethod
    def filter_included_headers(headers, headers_to_include):
        """
        Filters headers to log based on inclusion criteria.

        Args:
            headers (Dict[str, str]): The map of headers.
            headers_to_include (List[str]): The set of headers to include.

        Returns:
            Dict[str, str]: The extracted headers to log.
        """
        extracted_headers = {}
        for key, value in headers.items():
            if key.lower() in headers_to_include:
                extracted_headers[key] = value
        return extracted_headers

    @staticmethod
    def filter_excluded_headers(headers, headers_to_exclude):
        """
        Filters headers to log based on exclusion criteria.

        Args:
            headers (Dict[str, str]): The map of headers.
            headers_to_exclude (List[str]): The set of headers to exclude.

        Returns:
            Dict[str, str]: The extracted headers to log.
        """
        extracted_headers = {}
        for key, value in headers.items():
            if key.lower() not in headers_to_exclude:
                extracted_headers[key] = value
        return extracted_headers
