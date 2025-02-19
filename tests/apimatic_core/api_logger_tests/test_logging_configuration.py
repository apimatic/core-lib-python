import pytest
from typing import Dict, List, Any

from apimatic_core.logger.configuration.api_logging_configuration import ApiRequestLoggingConfiguration


class TestLogHelper:
    @staticmethod
    def create_sample_headers() -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

    @staticmethod
    def create_sample_request_logging_configuration(
            headers_to_include: List[str]=None, headers_to_exclude: List[str]=None, headers_to_unmask: List[str]=None
    ) -> ApiRequestLoggingConfiguration:
        return ApiRequestLoggingConfiguration(log_body=False, log_headers=False, include_query_in_path=False,
                                              headers_to_include=headers_to_include or [],
                                              headers_to_exclude=headers_to_exclude or [],
                                              headers_to_unmask=headers_to_unmask or [])

    def test_get_headers_to_log_include(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_include=["Authorization"])
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, False)
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_get_headers_to_log_exclude(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_exclude=["Authorization"])
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, False)
        assert "Authorization" not in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_get_headers_to_log_include_and_exclude(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_include=["Authorization"], headers_to_exclude=["Accept"])
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, False)
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_get_headers_to_log_sensitive_masking_enabled(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, True)
        assert "Authorization" in result.keys()
        assert "**Redacted**" == result.get("Authorization")

    def test_get_headers_to_log_sensitive_masking_disabled(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_get_headers_to_log_sensitive_masking_disabled_with_headers_to_unmask(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_unmask=["Authorization"])
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_get_headers_to_log_sensitive_masking_enabled_with_headers_to_unmask(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_unmask=["Authorization"])
        result: Dict[str, Any] = logging_config.get_loggable_headers(headers, True)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_extract_headers_to_log_include(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_include=["Authorization"])
        result: Dict[str, Any] = logging_config._extract_headers_to_log(headers)
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_extract_headers_to_log_exclude(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_exclude=["Authorization"])
        result: Dict[str, Any] = logging_config._extract_headers_to_log(headers)
        assert "Authorization" not in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_extract_headers_to_log_no_criteria(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config._extract_headers_to_log(headers)
        assert "Authorization" in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_mask_sensitive_headers_masking_enabled(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config._mask_sensitive_headers(headers, True)
        assert "Authorization" in result.keys()
        assert "**Redacted**" == result.get("Authorization")

    def test_mask_sensitive_headers_masking_enabled_with_headers_to_unmask(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_unmask=["Authorization"])
        result: Dict[str, Any] = logging_config._mask_sensitive_headers(headers, True)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_mask_sensitive_headers_masking_disable(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config._mask_sensitive_headers(headers, False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_mask_sensitive_headers_masking_disabled_with_headers_to_unmask(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_unmask=["Authorization"])
        result: Dict[str, Any] = logging_config._mask_sensitive_headers(headers, False)
        assert "Authorization" in result.keys()
        assert "Bearer token" == result.get("Authorization")

    def test_filter_included_headers(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_include=["Authorization"])
        result: Dict[str, Any] = logging_config._filter_included_headers(headers)
        assert "Authorization" in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_filter_included_headers_no_inclusion(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config._filter_included_headers(headers)
        assert "Authorization" not in result.keys()
        assert "Content-Type" not in result.keys()
        assert "User-Agent" not in result.keys()
        assert "Accept" not in result.keys()

    def test_filter_excluded_headers(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration(
            headers_to_exclude=["Authorization"])
        result: Dict[str, Any] = logging_config._filter_excluded_headers(headers)
        assert "Authorization" not in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()

    def test_filter_excluded_headers_no_exclusion(self):
        headers: Dict[str, str] = self.create_sample_headers()
        logging_config: ApiRequestLoggingConfiguration = self.create_sample_request_logging_configuration()
        result: Dict[str, Any] = logging_config._filter_excluded_headers(headers)
        assert "Authorization" in result.keys()
        assert "Content-Type" in result.keys()
        assert "User-Agent" in result.keys()
        assert "Accept" in result.keys()
