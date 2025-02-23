import logging
import os

import uvicorn
from fastapi import FastAPI
from ml_api.api.router import router

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn_log_level = os.environ.get("UVICORN_LOGLEVEL", "info").lower()
    log_level = os.environ.get("LOGLEVEL", "info").upper()

    logger.info(
        f"Starting server with log levels: UVICORN_LOGLEVEL={uvicorn_log_level}, LOGLEVEL={log_level}"
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=uvicorn_log_level,
    )
