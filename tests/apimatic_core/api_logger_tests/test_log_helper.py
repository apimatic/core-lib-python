import pytest
from apimatic_core.logger.configuration.api_logging_configuration import ApiRequestLoggingConfiguration
from apimatic_core.utilities.log_helper import LogHelper


class TestLogHelper:
    @staticmethod
    def create_sample_headers():
        # Create sample headers for testing
        return {
            "Accept": "application/json",
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

    @staticmethod
    def create_sample_request_logging_configuration(headers_to_include=None, headers_to_exclude=None,
                                                    headers_to_unmask=None):
        # Create a sample request logging configuration object for testing
        return ApiRequestLoggingConfiguration(log_body=False, log_headers=False, include_query_in_path=False,
                                              headers_to_include=headers_to_include or [],
                                              headers_to_exclude=headers_to_exclude or [],
                                              headers_to_unmask=headers_to_unmask or [])

    def test_get_headers_to_log_include(self):
        # Test get_headers_to_log with inclusion criteria
        headers = self.create_sample_headers()
        headers = {key.lower(): value for key, value in headers.items()}
        logging_config = self.create_sample_request_logging_configuration(headers_to_include=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result
        assert "Accept" not in result

    def test_get_headers_to_log_exclude(self):
        # Test get_headers_to_log with exclusion criteria
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_exclude=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" not in result
        assert "Accept" in result

    def test_get_headers_to_log_include_and_exclude(self):
        # Test get_headers_to_log with both inclusion and exclusion criteria
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_include=["Authorization"],
                                                                          headers_to_exclude=["Accept"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result
        assert "Accept" not in result

    def test_get_headers_to_log_sensitive_masking_enabled(self):
        # Test get_headers_to_log with sensitive header masking enabled
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_unmask=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, True)
        assert "Authorization" not in result.values()
        assert "**Redacted**" in result.values()

    def test_get_headers_to_log_sensitive_masking_disabled(self):
        # Test get_headers_to_log with sensitive header masking disabled
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_unmask=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result.values()
        assert "**Redacted**" not in result.values()

    def test_extract_headers_to_log_include(self):
        # Test extract_headers_to_log when headers are included
        headers = self.create_sample_headers()
        result = LogHelper.extract_headers_to_log(headers, ["Authorization"], [])
        assert "Authorization" in result
        assert "Accept" not in result

    def test_extract_headers_to_log_exclude(self):
        # Test extract_headers_to_log when headers are excluded
        headers = self.create_sample_headers()
        result = LogHelper.extract_headers_to_log(headers, [], ["Authorization"])
        assert "Authorization" not in result
        assert "Accept" in result

    def test_extract_headers_to_log_no_criteria(self):
        # Test extract_headers_to_log when no criteria are provided
        headers = self.create_sample_headers()
        result = LogHelper.extract_headers_to_log(headers, [], [])
        assert "Authorization" in result
        assert "Accept" in result

    def test_filter_sensitive_headers_masking_enabled(self):
        # Test filter_sensitive_headers with sensitive header masking enabled
        headers = self.create_sample_headers()
        result = LogHelper.filter_sensitive_headers(headers, ["Authorization"], True)
        assert "Authorization" not in result.values()
        assert "**Redacted**" in result.values()

    def test_filter_sensitive_headers_masking_disabled(self):
        # Test filter_sensitive_headers with sensitive header masking disabled
        headers = self.create_sample_headers()
        result = LogHelper.filter_sensitive_headers(headers, ["Authorization"], False)
        assert "Authorization" in result.values()
        assert "**Redacted**" not in result.values()

    def test_filter_sensitive_headers_unmask(self):
        # Test filter_sensitive_headers when headers need to be unmasked
        headers = self.create_sample_headers()
        result = LogHelper.filter_sensitive_headers(headers, ["Authorization"], True)
        assert "Authorization" not in result.values()
        assert "**Redacted**" in result.values()

    def test_extract_included_headers(self):
        # Test extract_included_headers when headers are included
        headers = self.create_sample_headers()
        result = LogHelper.extract_included_headers(headers, ["Authorization"])
        assert "Authorization" in result
        assert "Accept" not in result

    def test_extract_included_headers_no_inclusion(self):
        # Test extract_included_headers when no headers are included
        headers = self.create_sample_headers()
        result = LogHelper.extract_included_headers(headers, [])
        assert "Authorization" in result
        assert "Accept" in result

    def test_extract_excluded_headers(self):
        # Test extract_excluded_headers when headers are excluded
        headers = self.create_sample_headers()
        result = LogHelper.extract_excluded_headers(headers, ["Authorization"])
        assert "Authorization" not in result
        assert "Accept" in result

    def test_extract_excluded_headers_no_exclusion(self):
        # Test extract_excluded_headers when no headers are excluded
        headers = self.create_sample_headers()
        result = LogHelper.extract_excluded_headers(headers, [])
        assert "Authorization" in result
        assert "Accept" in result