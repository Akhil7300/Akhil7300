from fastapi import Header, HTTPException, status

from src.config import get_settings

settings = get_settings()


async def verify_admin_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return x_api_key
