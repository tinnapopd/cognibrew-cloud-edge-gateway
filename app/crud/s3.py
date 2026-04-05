import json
from typing import Any

from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logger import Logger

logger = Logger().get_logger()


def ensure_bucket(s3: Any) -> None:
    """Create the raw-data bucket if it does not already exist."""
    try:
        s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except ClientError:
        logger.info("Creating S3 bucket: %s", settings.S3_BUCKET_NAME)
        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)


def put_json(s3: Any, key: str, data: dict[str, Any] | list[Any]) -> str:
    """Upload a JSON document to S3 and return the key."""
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


def get_json(s3: Any, key: str) -> dict[str, Any] | list[Any]:
    """Download and parse a JSON object from S3."""
    obj = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    return json.loads(obj["Body"].read().decode())


def list_keys(s3: Any, prefix: str) -> list[str]:
    """List all object keys under a given prefix."""
    resp = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix)
    return [obj["Key"] for obj in resp.get("Contents", [])]


def delete_object(s3: Any, key: str) -> None:
    """Delete a single object from S3."""
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    logger.info("Deleted s3://%s/%s", settings.S3_BUCKET_NAME, key)


def delete_keys(s3: Any, keys: list[str]) -> int:
    """Delete multiple objects from S3. Returns count of deleted keys."""
    if not keys:
        return 0
    objects = [{"Key": k} for k in keys]
    s3.delete_objects(
        Bucket=settings.S3_BUCKET_NAME,
        Delete={"Objects": objects},
    )
    logger.info(
        "Deleted %d objects from s3://%s",
        len(keys),
        settings.S3_BUCKET_NAME,
    )
    return len(keys)
