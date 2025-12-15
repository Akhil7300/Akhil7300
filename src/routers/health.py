from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    status: str

@router.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok")
