from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
import logging
from .config import Settings
from .types import AutoscalerState
from .api import routes
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = Settings()
    state = AutoscalerState()
    state.http_client = httpx.AsyncClient(timeout=settings.proxy_timeout)

    # Store in app state for access in dependencies
    app.state.settings = settings
    app.state.state = state

    yield

    # Shutdown
    if state.http_client:
        await state.http_client.aclose()
    if state.shutdown_task:
        state.shutdown_task.cancel()
        try:
            await state.shutdown_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="vLLM Autoscaler",
    description="Autoscaler and proxy for vLLM deployments in Kubernetes",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
