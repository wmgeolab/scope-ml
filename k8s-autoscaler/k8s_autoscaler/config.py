from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import cached_property


class Settings(BaseSettings):
    """Application settings with validation and documentation."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    vllm_service_host: str = Field(
        default="vllm-svc", description="Hostname of the vLLM service"
    )
    vllm_service_port: str = Field(
        default="8000", description="Port of the vLLM service"
    )
    vllm_deployment: str = Field(
        default="vllm", description="Name of the vLLM deployment"
    )
    kubernetes_namespace: str = Field(
        default="default", description="Kubernetes namespace for the vLLM deployment"
    )
    inactivity_timeout: int = Field(
        default=900,
        description="Timeout in seconds before scaling down due to inactivity",
        gt=0,
    )
    activation_timeout: int = Field(
        default=120,
        description="Timeout in seconds while waiting for vLLM to become ready",
        gt=0,
    )
    proxy_timeout: float = Field(
        default=30.0, description="Timeout in seconds for proxy requests", gt=0
    )

    @cached_property
    def vllm_url_base(self) -> str:
        """Base URL for the vLLM service."""
        return f"http://{self.vllm_service_host}:{self.vllm_service_port}"

    @cached_property
    def kubectl_base_cmd(self) -> str:
        """Base kubectl command with namespace."""
        return f"kubectl -n {self.kubernetes_namespace}"
