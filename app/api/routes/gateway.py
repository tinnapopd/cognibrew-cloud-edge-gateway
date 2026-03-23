from fastapi import APIRouter, HTTPException

from app.crud.s3 import put_json
from app.core.logger import Logger
from app.models.schemas import BatchUpload, EnrollmentRequest, UploadResponse

logger = Logger().get_logger()

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/batch", response_model=UploadResponse)
async def receive_batch(payload: BatchUpload) -> UploadResponse:
    """Receive a daily batch of face-embedding vectors from an Edge device.

    Stores the entire batch as ``/{date}/{device_id}.json`` in S3.
    """
    s3_key = f"{payload.date}/{payload.device_id}.json"
    try:
        put_json(s3_key, payload.model_dump())
    except Exception as exc:
        logger.exception("Failed to store batch to S3")
        raise HTTPException(
            status_code=502, detail=f"S3 write failed: {exc}"
        ) from exc

    return UploadResponse(
        s3_key=s3_key,
        record_count=len(payload.vectors),
    )


@router.post("/enroll", response_model=UploadResponse)
async def enroll(payload: EnrollmentRequest) -> UploadResponse:
    """Accept an initial enrollment embedding (baseline vector) from Edge.

    Stores under ``/enrollments/{username}/{device_id}.json``.
    """
    s3_key = f"enrollments/{payload.username}/{payload.device_id}.json"
    data = {
        "username": payload.username,
        "embedding": payload.embedding,
        "device_id": payload.device_id,
    }
    try:
        put_json(s3_key, data)
    except Exception as exc:
        logger.exception("Failed to store enrollment to S3")
        raise HTTPException(
            status_code=502, detail=f"S3 write failed: {exc}"
        ) from exc

    return UploadResponse(s3_key=s3_key, record_count=1)
