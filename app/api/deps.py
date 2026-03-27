from collections.abc import Generator
from typing import Annotated, Any

import boto3
from fastapi import Depends

from app.core.config import settings


def get_s3_client() -> Generator[Any, None, None]:
    """Yield a boto3 S3 client, usable as a FastAPI dependency."""
    client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="ap-southeast-1",
    )
    yield client


S3Dep = Annotated[Any, Depends(get_s3_client)]
