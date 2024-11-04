import asyncio
import logging
import time
from fastapi import BackgroundTasks
from .types import PodPhase, AutoscalerState
from .config import Settings
from .kubernetes import KubeCommand

logger = logging.getLogger(__name__)


class VLLMManager:
    """Manager for vLLM deployment operations."""

    def __init__(self, settings: Settings, state: AutoscalerState, kube: KubeCommand):
        self.settings = settings
        self.state = state
        self.kube = kube

    async def ensure_running(self) -> bool:
        """Ensure vLLM is running, scaling up if necessary."""
        async with self.state.scaling_lock:
            if not await self.kube.deployment_exists():
                logger.info(f"Deployment {self.settings.vllm_deployment} not found")
                return False
            
            phase = await self.kube.get_pod_phase()
            if phase == PodPhase.RUNNING:
                return True

            logger.info(f"vLLM not running (phase: {phase}), scaling up")
            if not await self.kube.scale_deployment(1):
                return False

            return await self._wait_until_ready()

    async def _wait_until_ready(self) -> bool:
        """Wait for vLLM to become ready."""
        start_time = time.time()
        while time.time() - start_time < self.settings.activation_timeout:
            phase = await self.kube.get_pod_phase()
            if phase == PodPhase.RUNNING:
                return True
            if phase == PodPhase.FAILED:
                logger.error("Pod failed to start")
                return False
            await asyncio.sleep(2)
        logger.error("Timeout waiting for pod to become ready")
        return False

    async def monitor_inactivity(self):
        """Monitor for inactivity and scale down when timeout is reached."""
        try:
            while True:
                await asyncio.sleep(60)
                if not await self.kube.deployment_exists():
                    break
                
                current_replicas = await self.kube.get_replicas()
                if (
                    time.time() - self.state.last_activity
                    > self.settings.inactivity_timeout
                    and current_replicas > 0
                ):
                    logger.info(
                        f"Scaling down vLLM after {self.settings.inactivity_timeout}s inactivity"
                    )
                    await self.kube.scale_deployment(0)
                    break
        except Exception as e:
            logger.error(f"Error in inactivity monitor: {e}")
        finally:
            self.state.shutdown_task = None

    def reset_inactivity_timer(self, background_tasks: BackgroundTasks):
        """Reset inactivity timer and ensure monitoring task is running."""
        self.state.last_activity = time.time()
        if self.state.shutdown_task is None:
            self.state.shutdown_task = asyncio.create_task(self.monitor_inactivity())
            background_tasks.add_task(lambda: self.state.shutdown_task)
