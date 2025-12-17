from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database import engine

jobstores = {"default": SQLAlchemyJobStore(engine=engine)}

scheduler = AsyncIOScheduler(jobstores=jobstores)


def start_scheduler() -> None:
    scheduler.start()


def shutdown_scheduler() -> None:
    scheduler.shutdown()
