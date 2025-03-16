import asyncio
import logging
import time

from fastapi import BackgroundTasks

from .config import ServiceConfig, Settings
from .kubernetes import KubeCommand
from .types import AutoscalerState, PodPhase

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manager for vLLM deployment operations."""

    def __init__(self, settings: Settings, state: AutoscalerState, kube: KubeCommand):
        self.settings = settings
        self.state = state
        self.kube = kube

    async def ensure_running(self, service_name: str) -> bool:
        """Ensure vLLM is running, scaling up if necessary."""

        service_config = self.settings.services[service_name]
        service_lock = self.state.get_lock(service_name)

        async with service_lock:
            if not await self.kube.deployment_exists(service_config):
                logger.info(f"Deployment {service_config.deployment_name} not found")
                return False

            phase = await self.kube.get_pod_phase(service_config)
            if phase == PodPhase.RUNNING:
                return True

            logger.info(
                f"{service_config.name} not running (phase: {phase}), scaling up"
            )
            if not await self.kube.scale_deployment(1, service_config):
                return False

            return await self._wait_until_ready(service_config)

    async def _wait_until_ready(self, service_config: ServiceConfig) -> bool:
        """Wait for vLLM to become ready."""
        start_time = time.time()
        while time.time() - start_time < service_config.activation_timeout:
            phase = await self.kube.get_pod_phase(service_config)
            if phase == PodPhase.RUNNING:
                return True
            if phase == PodPhase.FAILED:
                logger.error("Pod failed to start")
                return False
            await asyncio.sleep(2)
        logger.error("Timeout waiting for pod to become ready")
        return False

    async def inactivity_downscale_task(self, service_name: str):
        """Monitor for inactivity and scale down when timeout is reached."""
        service_config = self.settings.services[service_name]
        service_state = self.state.get_service_state(service_name)
        service_lock = self.state.get_lock(service_name)

        try:
            while True:
                await asyncio.sleep(60)  # Only check every 60 seconds
                if not await self.kube.deployment_exists(service_config):
                    break

                current_replicas = await self.kube.get_replicas(service_config)
                if (
                    time.time() - service_state.last_activity
                    > service_config.inactivity_timeout
                    and current_replicas > 0
                ):
                    logger.info(
                        f"More than {service_config.inactivity_timeout}s since last activity, scaling down."
                    )

                    await self.kube.scale_deployment(0, service_config)
                    break
        except Exception as e:
            logger.error(f"Error in inactivity monitor: {e}")
        finally:
            service_state.inactivity_task = None

    def reset_inactivity_timer(
        self, service_name: str, background_tasks: BackgroundTasks
    ):
        """Reset inactivity timer and ensure monitoring task is running."""

        service_state = self.state.get_service_state(service_name)
        service_state.last_activity = time.time()

        if service_state.inactivity_task is None:
            service_state.inactivity_task = asyncio.create_task(
                self.inactivity_downscale_task(service_name)
            )
            background_tasks.add_task(lambda: service_state.inactivity_task)
