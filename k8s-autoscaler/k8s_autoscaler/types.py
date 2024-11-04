from enum import Enum
from dataclasses import dataclass, field
import asyncio
from typing import Optional, ClassVar
import httpx
import time


class PodPhase(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


@dataclass
class AutoscalerState:
    """Global state management for the autoscaler."""

    last_activity: float = field(default_factory=time.time)
    shutdown_task: Optional[asyncio.Task] = None
    http_client: Optional[httpx.AsyncClient] = None
    scaling_lock: ClassVar[asyncio.Lock] = asyncio.Lock()
