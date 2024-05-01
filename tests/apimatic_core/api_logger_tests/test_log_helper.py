import pytest
from apimatic_core.logger.configuration.api_logging_configuration import ApiRequestLoggingConfiguration
from apimatic_core.utilities.log_helper import LogHelper


class TestLogHelper:
    @staticmethod
    def create_sample_headers():
        return {
            "Accept": "application/json",
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

    @staticmethod
    def create_sample_request_logging_configuration(headers_to_include=None, headers_to_exclude=None,
                                                    headers_to_unmask=None):
        return ApiRequestLoggingConfiguration(log_body=False, log_headers=False, include_query_in_path=False,
                                              headers_to_include=headers_to_include or [],
                                              headers_to_exclude=headers_to_exclude or [],
                                              headers_to_unmask=headers_to_unmask or [])

    def test_get_headers_to_log_include(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_include=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_get_headers_to_log_exclude(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_exclude=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" not in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_get_headers_to_log_include_and_exclude(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_include=["Authorization"],
                                                                          headers_to_exclude=["Accept"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_get_headers_to_log_sensitive_masking_enabled(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration()
        result = LogHelper.get_headers_to_log(logging_config, headers, True)
        assert "Authorization" in result.keys()
        assert "**Redacted**" == result.get("Authorization")

    def test_get_headers_to_log_sensitive_masking_disabled(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration()
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_get_headers_to_log_sensitive_masking_disabled_with_headers_to_unmask(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_unmask=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_get_headers_to_log_sensitive_masking_enabled_with_headers_to_unmask(self):
        headers = self.create_sample_headers()
        logging_config = self.create_sample_request_logging_configuration(headers_to_unmask=["Authorization"])
        result = LogHelper.get_headers_to_log(logging_config, headers, True)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_extract_headers_to_log_include(self):
        headers = self.create_sample_headers()
        result = LogHelper.extract_headers_to_log(headers, ["authorization"], [])
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_extract_headers_to_log_exclude(self):
        headers = self.create_sample_headers()
        result = LogHelper.extract_headers_to_log(headers, [], ["authorization"])
        assert "Authorization" not in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_extract_headers_to_log_no_criteria(self):
        # Test extract_headers_to_log when no criteria are provided
        headers = self.create_sample_headers()
        result = LogHelper.extract_headers_to_log(headers, [], [])
        assert "Authorization" in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_mask_sensitive_headers_masking_enabled(self):
        headers = self.create_sample_headers()
        result = LogHelper.mask_sensitive_headers(headers, [], True)
        assert "Authorization" in result.keys()
        assert "**Redacted**" == result.get("Authorization")

    def test_mask_sensitive_headers_masking_enabled_with_headers_to_unmask(self):
        headers = self.create_sample_headers()
        result = LogHelper.mask_sensitive_headers(headers, ["authorization"], True)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_mask_sensitive_headers_masking_disable(self):
        headers = self.create_sample_headers()
        result = LogHelper.mask_sensitive_headers(headers, [], False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_mask_sensitive_headers_masking_disabled_with_headers_to_unmask(self):
        headers = self.create_sample_headers()
        result = LogHelper.mask_sensitive_headers(headers, ["authorization"], False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_filter_included_headers(self):
        headers = self.create_sample_headers()
        result = LogHelper.filter_included_headers(headers, ["authorization"])
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_filter_included_headers_no_inclusion(self):
        headers = self.create_sample_headers()
        result = LogHelper.filter_included_headers(headers, [])
        assert "Authorization" not in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_filter_excluded_headers(self):
        headers = self.create_sample_headers()
        result = LogHelper.filter_excluded_headers(headers, ["authorization"])
        assert "Authorization" not in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_filter_excluded_headers_no_exclusion(self):
        headers = self.create_sample_headers()
        result = LogHelper.filter_excluded_headers(headers, [])
        assert "Authorization" in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()
