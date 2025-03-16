import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .api import routes
from .config import Settings
from .types import AutoscalerState

# Configure logging
app_log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, app_log_level),
    format="%(asctime)s - %(levelname)s - %(message)s",
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

    for state in state.services.values():
        if state.inactivity_task:
            # If there are any inactivity tasks, cancel them when the app is shutting down
            state.inactivity_task.cancel()


def create_app():
    app = FastAPI(
        title="vLLM Autoscaler",
        description="Autoscaler and proxy for vLLM deployments in Kubernetes",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(routes.router)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn_log_level = os.getenv("UVICORN_LOG_LEVEL", "debug")

    app = create_app()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=uvicorn_log_level)
