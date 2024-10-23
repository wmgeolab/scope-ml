from fastapi import FastAPI, Response, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import subprocess
from asyncio.subprocess import Process
import logging
import time
import os
from typing import Optional, TypedDict, Literal, AsyncGenerator, cast
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Type definitions
PodPhase = Literal["Pending", "Running", "Succeeded", "Failed", "Unknown"]


class CommandResult(TypedDict):
    success: bool
    output: str
    error: str


@dataclass
class Config:
    vllm_service_host: str
    vllm_service_port: str
    vllm_deployment: str
    kubernetes_namespace: str
    inactivity_timeout: int
    activation_timeout: int


# Load configuration from environment
config = Config(
    vllm_service_host=os.getenv("VLLM_SERVICE_HOST", "vllm-svc"),
    vllm_service_port=os.getenv("VLLM_SERVICE_PORT", "8000"),
    vllm_deployment=os.getenv("VLLM_DEPLOYMENT_NAME", "vllm"),
    kubernetes_namespace=os.getenv("KUBERNETES_NAMESPACE", "default"),
    inactivity_timeout=int(os.getenv("INACTIVITY_TIMEOUT", "900")),
    activation_timeout=int(os.getenv("ACTIVATION_TIMEOUT", "120")),
)


# Global state
class AutoscalerState:
    def __init__(self):
        self.last_activity: float = time.time()
        self.shutdown_task: Optional[asyncio.Task] = None
        self.http_client: Optional[httpx.AsyncClient] = None


state = AutoscalerState()


async def execute_command(cmd: str) -> CommandResult:
    """Execute a shell command and return structured result."""
    try:
        process: Process = await asyncio.create_subprocess_shell(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        return CommandResult(
            success=process.returncode == 0,
            output=stdout.decode().strip(),
            error=stderr.decode().strip(),
        )
    except Exception as e:
        logger.error(f"Failed to execute command: {str(e)}")
        return CommandResult(success=False, output="", error=str(e))


async def check_vllm_status() -> tuple[bool, PodPhase]:
    """Check if VLLM deployment is running and ready."""
    cmd = f"kubectl get pods -n {config.kubernetes_namespace} -l app=vllm -o jsonpath='{{.items[0].status.phase}}'"
    result = await execute_command(cmd)

    if not result["success"]:
        return False, "Unknown"

    phase = result["output"]
    if not phase:
        return False, "Unknown"

    return phase == "Running", cast(PodPhase, phase)


async def scale_vllm(replicas: int) -> bool:
    """Scale VLLM deployment to specified number of replicas."""
    cmd = f"kubectl scale deployment -n {config.kubernetes_namespace} {config.vllm_deployment} --replicas={replicas}"
    result = await execute_command(cmd)

    if not result["success"]:
        logger.error(f"Failed to scale VLLM: {result['error']}")

    return result["success"]


async def wait_for_vllm_ready() -> bool:
    """Wait for VLLM to become ready within timeout period."""
    start_time = time.time()
    while time.time() - start_time < config.activation_timeout:
        is_running, phase = await check_vllm_status()
        if is_running:
            return True
        logger.info(f"Waiting for VLLM to be ready. Current phase: {phase}")
        await asyncio.sleep(2)
    return False


async def monitor_inactivity():
    """Monitor for inactivity and scale down when timeout is reached."""
    try:
        while True:
            await asyncio.sleep(60)  # Check every minute
            if time.time() - state.last_activity > config.inactivity_timeout:
                logger.info(
                    f"Inactivity timeout of {config.inactivity_timeout}s reached, scaling down VLLM"
                )
                if await scale_vllm(0):
                    logger.info("VLLM scaled down successfully")
                else:
                    logger.error("Failed to scale down VLLM")
                break
    except Exception as e:
        logger.error(f"Error in inactivity monitor: {str(e)}")
    finally:
        state.shutdown_task = None


def reset_inactivity_timer(background_tasks: BackgroundTasks):
    """Reset the inactivity timer and start monitoring if needed."""
    state.last_activity = time.time()

    if state.shutdown_task is None:
        state.shutdown_task = asyncio.create_task(monitor_inactivity())
        background_tasks.add_task(lambda: state.shutdown_task)


@asynccontextmanager
async def get_http_client():
    """Get or create HTTP client."""
    if state.http_client is None:
        state.http_client = httpx.AsyncClient(timeout=30.0)
    try:
        yield state.http_client
    finally:
        pass  # Keep client alive for reuse


async def stream_response(response: httpx.Response) -> AsyncGenerator[bytes, None]:
    """Stream response content."""
    async for chunk in response.aiter_bytes():
        yield chunk


app = FastAPI(title="VLLM Autoscaler")


@app.on_event("startup")
async def startup_event():
    """Initialize HTTP client on startup."""
    state.http_client = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    if state.http_client:
        await state.http_client.aclose()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    is_running, phase = await check_vllm_status()
    return {"status": "healthy", "vllm_status": phase, "vllm_running": is_running}


@app.get("/{path:path}")
async def proxy_request(
    path: str,
    response: Response,
    background_tasks: BackgroundTasks,
    raw_query_string: str = "",
) -> StreamingResponse:
    """Proxy requests to VLLM service, handling activation as needed."""
    try:
        # Check if VLLM is running
        is_running, phase = await check_vllm_status()
        if not is_running:
            logger.info(
                f"VLLM not running (phase: {phase}), starting activation sequence"
            )

            # Scale up VLLM
            if not await scale_vllm(1):
                raise HTTPException(
                    status_code=503, detail="Failed to activate VLLM service"
                )

            # Wait for VLLM to become ready
            if not await wait_for_vllm_ready():
                raise HTTPException(
                    status_code=503,
                    detail=f"VLLM service activation timeout after {config.activation_timeout}s",
                )

            logger.info("VLLM activation completed successfully")

        # Reset inactivity timer
        reset_inactivity_timer(background_tasks)

        # Proxy the request to VLLM
        query = f"?{raw_query_string}" if raw_query_string else ""
        vllm_url = f"http://{config.vllm_service_host}:{config.vllm_service_port}/{path}{query}"

        async with get_http_client() as client:
            vllm_response = await client.get(vllm_url)

            # Create streaming response
            return StreamingResponse(
                stream_response(vllm_response),
                status_code=vllm_response.status_code,
                headers=dict(vllm_response.headers),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
