import json
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logger import Logger

logger = Logger().get_logger()


def _client() -> Any:
    """Return a lazily-initialised boto3 S3 client."""
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="ap-southeast-1",
    )


def ensure_bucket() -> None:
    """Create the raw-data bucket if it does not already exist."""
    s3 = _client()
    try:
        s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except ClientError:
        logger.info("Creating S3 bucket: %s", settings.S3_BUCKET_NAME)
        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)


def put_json(key: str, data: dict[str, Any] | list[Any]) -> str:
    """Upload a JSON document to S3 and return the key."""
    s3 = _client()
    body = json.dumps(data, default=str)
    s3.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
    logger.info(
        "Stored %d bytes → s3://%s/%s",
        len(body),
        settings.S3_BUCKET_NAME,
        key,
    )
    return key


def get_json(key: str) -> dict[str, Any] | list[Any]:
    """Download and parse a JSON object from S3."""
    s3 = _client()
    obj = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    return json.loads(obj["Body"].read().decode())


def list_keys(prefix: str) -> list[str]:
    """List all object keys under a given prefix."""
    s3 = _client()
    resp = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix)
    return [obj["Key"] for obj in resp.get("Contents", [])]
