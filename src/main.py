import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.database import init_db
from src.logging import setup_logging
from src.routers import coordinator, health
from src.services.scheduler import shutdown_scheduler, start_scheduler
from src.services.scheduler_manager import sync_all_jobs

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application")
    init_db()
    start_scheduler()
    sync_all_jobs()
    yield
    # Shutdown
    logger.info("Shutting down application")
    shutdown_scheduler()

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# Exception Middleware
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.4f}s"
        )
        
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

app.include_router(health.router)
app.include_router(coordinator.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
