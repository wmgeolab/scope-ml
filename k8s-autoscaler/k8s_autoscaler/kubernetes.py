import asyncio
import logging
import subprocess

from .config import ServiceConfig, Settings
from .types import PodPhase

logger = logging.getLogger(__name__)


class KubeCommand:
    """Kubectl command builder and executor."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute(self, cmd: str) -> tuple[bool, str]:
        """Execute a kubectl command and return success status and output."""
        full_cmd = f"{self.settings.kubectl_base_cmd} {cmd}"
        logger.debug(f"Executing kubectl command: {full_cmd}")

        try:
            process = await asyncio.create_subprocess_shell(
                full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            output = stdout.decode().strip() if success else stderr.decode().strip()
            if not success:
                logger.error(f"kubectl command failed: {output}")

            logger.debug(f"Command output: `{output}`")
            return success, output

        except Exception as e:
            logger.error(f"kubectl command failed: {e}")
            return False, str(e)

    async def get_pod_phase(self, service: ServiceConfig) -> PodPhase:
        """Get the phase of the vLLM pod."""
        success, output = await self.execute(
            f"get pods -l {service.selector_label}={service.selector_value} -o jsonpath='{{.items[*].status.phase}}'"
        )

        if not success or not output:
            logger.info(f"No pods found for service {service.name}")
            return PodPhase.UNKNOWN

        # If multiple pods exist, get the first non-failed one
        phases = output.split()
        for phase in phases:
            try:
                pod_phase = PodPhase(phase)
                if pod_phase != PodPhase.FAILED:
                    return pod_phase
            except ValueError:
                logger.warning(f"Unknown pod phase {phase} for service {service.name}")

        return PodPhase.UNKNOWN

    async def scale_deployment(self, replicas: int, service: ServiceConfig) -> bool:
        """Scale vLLM deployment to specified replicas."""
        if replicas < 0:
            logger.error(f"Invalid replica count: {replicas}")
            return False

        success, output = await self.execute(
            f'patch deployment {service.deployment_name} -p \'{{"spec":{{"replicas":{replicas}}}}}\''
        )

        if success:
            logger.info(
                f"Successfully scaled deployment {service.deployment_name} to {replicas} replicas"
            )

        return success

    async def get_replicas(self, service: ServiceConfig) -> int:
        """Get desired replica count."""
        cmd = (
            f"get deployment {service.deployment_name} "
            "-o jsonpath='{.spec.replicas}'"
        )
        success, output = await self.execute(cmd)
        if success and output:
            try:
                return int(output)
            except ValueError:
                logger.error(
                    f"Failed to parse replica count {output} for deployment {service.deployment_name}"
                )
        return -1

    async def deployment_exists(self, service: ServiceConfig) -> bool:
        """Check if the vLLM deployment exists."""
        cmd = f"get deployment {service.deployment_name} --no-headers"
        success, _ = await self.execute(cmd)
        return success
