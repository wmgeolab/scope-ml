import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum

import httpx


class PodPhase(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


@dataclass
class ServiceState:
    """Autoscaling state for an individual service."""

    name: str
    last_activity: float = field(default_factory=time.time)
    inactivity_task: asyncio.Task | None = None
    # scaling_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


@dataclass
class AutoscalerState:
    """Global state management for the autoscaler."""

    services: dict[str, ServiceState] = field(default_factory=dict)
    http_client: httpx.AsyncClient | None = None
    scaling_locks: dict[str, asyncio.Lock] = field(default_factory=dict)

    def get_service_state(self, service_name: str) -> ServiceState:
        """Get the state for a specific service."""
        if service_name not in self.services:
            self.services[service_name] = ServiceState(name=service_name)
            self.scaling_locks[service_name] = asyncio.Lock()

        return self.services[service_name]

    def get_lock(self, service_name: str) -> asyncio.Lock:
        return self.scaling_locks[service_name]
