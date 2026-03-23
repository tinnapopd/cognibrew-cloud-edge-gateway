from fastapi import APIRouter

from app.api.routes import gateway, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(gateway.router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT == "local":
    # Placeholder for local environment specific routes
    pass
