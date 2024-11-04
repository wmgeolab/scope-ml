import asyncio
import subprocess
import logging
from .types import PodPhase
from .config import Settings

logger = logging.getLogger(__name__)


class KubeCommand:
    """Kubectl command builder and executor."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute(self, cmd: str) -> tuple[bool, str]:
        """Execute a kubectl command and return success status and output."""
        full_cmd = f"{self.settings.kubectl_base_cmd} {cmd}"
        try:
            process = await asyncio.create_subprocess_shell(
                full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            output = stdout.decode().strip() if success else stderr.decode().strip()
            if not success:
                logger.error(f"kubectl command failed: {output}")
            return success, output
        except Exception as e:
            logger.error(f"kubectl command failed: {e}")
            return False, str(e)

    async def get_pod_phase(self) -> PodPhase:
        """Get the phase of the vLLM pod."""
        success, output = await self.execute(
            "get pods -l app=vllm -o jsonpath='{.items[0].status.phase}'"
        )
        try:
            return PodPhase(output) if success and output else PodPhase.UNKNOWN
        except ValueError:
            logger.warning(f"Unknown pod phase: {output}")
            return PodPhase.UNKNOWN

    async def scale_deployment(self, replicas: int) -> bool:
        """Scale vLLM deployment to specified replicas."""
        if replicas < 0:
            logger.error(f"Invalid replica count: {replicas}")
            return False

        success, output = await self.execute(
            f"scale deployment {self.settings.vllm_deployment} --replicas={replicas}"
        )
        if success:
            logger.info(f"Successfully scaled deployment to {replicas} replicas")
        return success

    async def get_replicas(self) -> tuple[int, int]:
        """Get current and desired replica counts."""
        cmd = (
            f"get deployment {self.settings.vllm_deployment} "
            "-o jsonpath='{.status.replicas} {.spec.replicas}'"
        )
        success, output = await self.execute(cmd)
        if success and output:
            try:
                current, desired = map(int, output.split())
                return current, desired
            except ValueError:
                logger.error(f"Failed to parse replica counts: {output}")
        return -1, -1
