from functools import cached_property
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseModel):
    """Configuration for a single managed service with validation."""

    name: str
    deployment_name: str
    selector_label: str = "app"
    selector_value: str
    service_host: str
    service_port: str
    namespace: str | None = None
    inactivity_timeout: int
    activation_timeout: int

    @cached_property
    def url_base(self) -> str:
        """Base URL for the service."""
        return f"http://{self.service_host}:{self.service_port}"


class Settings(BaseSettings):
    """Application settings with validation and documentation."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    default_kubernetes_namespace: str = Field(
        default="default", description="Kubernetes namespace for the vLLM deployment"
    )
    default_inactivity_timeout: int = Field(
        default=900,
        description="Timeout in seconds before scaling down due to inactivity",
        gt=0,
    )
    default_activation_timeout: int = Field(
        default=120,
        description="Timeout in seconds while waiting for vLLM to become ready",
        gt=0,
    )
    proxy_timeout: float = Field(
        default=30.0, description="Timeout in seconds for proxy requests", gt=0
    )
    services_config_path: str | Path = Field(
        default="services.yaml", description="Path to the services configuration file"
    )

    services: dict[str, ServiceConfig] = {}

    def model_post_init(self, __context: Any) -> None:
        """Override the model_post_init method to load service configurations after initialization."""
        self.load_service_configs()

    @cached_property
    def kubectl_base_cmd(self) -> str:
        """Base kubectl command with namespace."""
        return f"kubectl -n {self.default_kubernetes_namespace}"

    def load_service_configs(self) -> None:
        """
        Loads service configurations from a YAML file specified by `self.services_config_path`.

        This method reads the YAML configuration file, validates its structure, and populates
        the `self.services` dictionary with `ServiceConfig` instances.

        Raises:
            FileNotFoundError: If the configuration file does not exist at the specified path.

        Notes:
            - The configuration file should contain a dictionary with a key "services" that maps
              to another dictionary of service configurations.
            - If the "services" key is not present, the entire file content is treated as the
              services dictionary.
            - Each service configuration must be a dictionary. If a service configuration does
              not contain a "name" key, the service name is added to the configuration.

        Example:
            Given a YAML file with the following content:
            ```
            services:
              service1:
                key1: value1
                key2: value2
              service2:
                key1: value3
                key2: value4
            ```
            The `self.services` dictionary will be populated as:
            ```
            {
                "service1": ServiceConfig(name="service1", key1="value1", key2="value2"),
                "service2": ServiceConfig(name="service2", key1="value3", key2="value4")
            }
            ```
        """
        config_path = Path(self.services_config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config path {config_path} not found")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        if "services" in data and isinstance(
            data["services"], dict
        ):  # Check if 'services' is a dictionary
            services_data = data["services"]
        else:
            services_data = data

        for service_name, service_data in services_data.items():
            if "name" not in service_data:
                service_data["name"] = service_name

            self.services[service_name] = ServiceConfig(**service_data)
