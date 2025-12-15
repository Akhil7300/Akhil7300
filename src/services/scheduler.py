from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database import engine

# We can store jobs in the database so they persist across restarts
jobstores = {
    'default': SQLAlchemyJobStore(engine=engine)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

def start_scheduler():
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
