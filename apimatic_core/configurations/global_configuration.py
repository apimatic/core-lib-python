from typing import Dict, Optional, Callable, Any

from apimatic_core_interfaces.authentication.authentication import Authentication
from pydantic import validate_call, BaseModel, Field

from apimatic_core.http.configurations.http_client_configuration import HttpClientConfiguration
from apimatic_core.types.error_case import ErrorCase
from apimatic_core.utilities.api_helper import ApiHelper


class GlobalConfiguration(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    http_client_configuration: HttpClientConfiguration = Field(default_factory=HttpClientConfiguration)
    global_errors: Dict[str, ErrorCase] = Field(default_factory=dict)
    global_headers: Dict[str, Any] = Field(default_factory=dict)
    additional_headers: Dict[str, Any] = Field(default_factory=dict)
    auth_managers: Dict[str, Authentication] = Field(default_factory=dict)
    base_uri_executor: Optional[Callable[[Any], Optional[str]]] = None

    @validate_call
    def get_base_uri(self, server: Any = None) -> Optional[str]:
        if self.base_uri_executor is None:
            return None

        return self.base_uri_executor(server)

    def set_global_error(self, key: str, error_case: ErrorCase):
        self.global_errors[key] = error_case

    def set_global_header(self, key: str, value: str):
        self.global_headers[key] = value

    def set_additional_header(self, key: str, value: str):
        self.additional_headers[key] = value

    def add_user_agent(self, user_agent: str, user_agent_parameters: Optional[Dict[str, Dict[str, Any]]] = None):
        if user_agent_parameters:
            user_agent = ApiHelper.append_url_with_template_parameters(
                user_agent, user_agent_parameters
            ).replace('  ', ' ')
        if user_agent:
            self.global_headers['user-agent'] = user_agent
