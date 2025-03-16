from fastapi import (
    APIRouter,
    Request,
    Response,
    BackgroundTasks,
    HTTPException,
    status,
    Depends,
)
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import logging
import time
from typing import AsyncGenerator
from ..types import AutoscalerState, PodPhase
from ..config import Settings
from ..kubernetes import KubeCommand
from ..manager import ServiceManager
from ..dependencies import get_settings, get_state, get_kube, get_service_manager

logger = logging.getLogger(__name__)

router = APIRouter()


async def stream_response(response: httpx.Response) -> AsyncGenerator[bytes, None]:
    """Stream response content."""
    try:
        async for chunk in response.aiter_bytes():
            yield chunk
    except httpx.HTTPError as e:
        logger.error(f"Error streaming response: {e}")
        raise HTTPException(status_code=502, detail="Error streaming from vLLM service")


# @router.get("/health")
# async def health_check(
#     kube: KubeCommand = Depends(get_kube), state: AutoscalerState = Depends(get_state)
# ):
#     """Health check endpoint."""
#     phase = await kube.get_pod_phase()
#     current_replicas = await kube.get_replicas()
#     return {
#         "status": "healthy",
#         "vllm_status": phase,
#         "vllm_running": phase == PodPhase.RUNNING,
#         "current_replicas": current_replicas,
#         # "desired_replicas": desired_replicas,
#         "last_activity": time.strftime(
#             "%Y-%m-%d %H:%M:%S", time.localtime(state.last_activity)
#         ),
#     }


@router.post("/scale/{service_name}/{replicas}")
async def scale(
    replicas: int,
    service_name: str,
    background_tasks: BackgroundTasks,
    kube: KubeCommand = Depends(get_kube),
    settings: Settings = Depends(get_settings),
    service_manager: ServiceManager = Depends(get_service_manager),
) -> JSONResponse:
    """
    Manually scale the vLLM deployment.

    Args:
        replicas (int): The number of replicas to scale the deployment to. Must be non-negative.
        service_name (str): The name of the service to scale.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        kube (KubeCommand, optional): Dependency injection for Kubernetes commands. Defaults to Depends(get_kube).
        settings (Settings, optional): Dependency injection for application settings. Defaults to Depends(get_settings).
        service_manager (ServiceManager, optional): Dependency injection for the service manager. Defaults to Depends(get_service_manager).

    Returns:
        JSONResponse: A JSON response indicating the result of the scaling operation.

    Raises:
        HTTPException: If the replica count is negative or if scaling the deployment fails.
    """
    if replicas < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Replica count must be non-negative",
        )

    service_config = settings.services[service_name]
    if not await kube.scale_deployment(replicas, service_config):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scale deployment",
        )

    if replicas > 0:
        service_manager.reset_inactivity_timer(service_name, background_tasks)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Scaling deployment to {replicas} replicas"},
    )


# @router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
# async def proxy_request(
#     request: Request,
#     path: str,
#     background_tasks: BackgroundTasks,
#     settings: Settings = Depends(get_settings),
#     state: AutoscalerState = Depends(get_state),
#     vllm_manager: VLLMManager = Depends(get_vllm_manager),
# ) -> StreamingResponse:
#     """Proxy requests to vLLM service, handling activation as needed."""
#     try:
#         if not await vllm_manager.ensure_running():
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail=f"vLLM service activation failed after {settings.activation_timeout}s",
#             )

#         vllm_manager.reset_inactivity_timer(background_tasks)

#         if not state.http_client:
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail="HTTP client not initialized",
#             )

#         # Forward the request to vLLM
#         url = f"{settings.vllm_url_base}/{path}"
#         headers = dict(request.headers)
#         headers.pop("host", None)  # Remove host header to avoid conflicts

#         vllm_response = await state.http_client.request(
#             method=request.method,
#             url=url,
#             headers=headers,
#             content=await request.body(),
#             params=request.query_params,
#         )

#         return StreamingResponse(
#             stream_response(vllm_response),
#             status_code=vllm_response.status_code,
#             headers=dict(vllm_response.headers),
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error processing request: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error",
#         )
