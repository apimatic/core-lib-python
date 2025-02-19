from apimatic_core_interfaces.http.http_client import HttpClient
from pydantic import BaseModel, Field
from requests import Session
from typing import List, Optional

from apimatic_core.http.http_callback import HttpCallBack
from apimatic_core.logger.configuration.api_logging_configuration import ApiLoggingConfiguration


class HttpClientConfiguration(BaseModel):  # pragma: no cover
    """A class used for configuring the SDK by a user.
    """

    class Config:
        arbitrary_types_allowed = True

    http_client: Optional[HttpClient] = None
    http_client_instance: Optional[Session] = None
    override_http_client_configuration: bool = False
    http_callback: Optional[HttpCallBack] = None
    timeout: int = 60
    max_retries: int = 0
    backoff_factor: float = 2
    retry_statuses: Optional[List[int]] = Field(default_factory=lambda: [
        408, 413, 429, 500, 502, 503, 504, 521, 522, 524])
    retry_methods: Optional[List[str]] = Field(default_factory=lambda: ['GET', 'PUT'])
    logging_configuration: Optional[ApiLoggingConfiguration] = None