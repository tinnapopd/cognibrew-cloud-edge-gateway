from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.logger import Logger
from app.crud.s3 import ensure_bucket

logger = Logger().get_logger()


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup: ensure the S3 bucket exists."""
    ensure_bucket()
    logger.info("Edge Gateway ready")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Receives daily batch vectors from Edge. "
        "Validates payload schema. Stores raw data to S3."
    ),
    version="0.1.0",
    openapi_url=f"{settings.API_PREFIX_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_PREFIX_STR)
