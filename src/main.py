import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.database import init_db
from src.logging import setup_logging
from src.routers import health, youtube
from src.services.scheduler import shutdown_scheduler, start_scheduler

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting up application")
    init_db()
    start_scheduler()
    yield
    logger.info("Shutting down application")
    shutdown_scheduler()


settings = get_settings()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            "Request: %s %s - Status: %s - Duration: %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response
    except Exception as exc:  # noqa: BLE001
        logger.error("Unhandled exception: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )


app.include_router(health.router)
app.include_router(youtube.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
