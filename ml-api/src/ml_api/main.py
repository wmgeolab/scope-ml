import logging
import os

import uvicorn
import weave
from fastapi import FastAPI
from llama_index.core import set_global_handler
from ml_api.api.router import router
from ml_api.config import settings

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

for logger_name in settings.SUPPRESS_LOGGERS:
    suppress_logger = logging.getLogger(logger_name).setLevel(settings.SUPPRESSED_LEVEL)

set_global_handler("simple")

weave.init("ml-api")

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
