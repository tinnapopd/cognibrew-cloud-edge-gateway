from fastapi import APIRouter, HTTPException

from app.api.deps import S3Dep
from app.crud.s3 import delete_keys, get_json, list_keys, put_json
from app.core.logger import Logger
from app.models.schemas import (
    BatchUpload,
    CreateFacesRequest,
    DeleteFacesRequest,
    DeleteFacesResponse,
    FaceRecord,
    GetFacesRequest,
    GetFacesResponse,
    UploadResponse,
)

logger = Logger().get_logger()

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/batch", response_model=UploadResponse)
async def receive_batch(s3: S3Dep, payload: BatchUpload) -> UploadResponse:
    """Receive a daily batch of face-embedding vectors from an Edge device.

    Stores the entire batch as ``/{date}/{device_id}.json`` in S3.
    """
    s3_key = f"{payload.date}/{payload.device_id}.json"
    try:
        put_json(s3, s3_key, payload.model_dump())
    except Exception as exc:
        logger.exception("Failed to store batch to S3")
        raise HTTPException(
            status_code=502, detail=f"S3 write failed: {exc}"
        ) from exc

    return UploadResponse(
        s3_key=s3_key,
        record_count=len(payload.vectors),
    )


# ── Face CRUD ────────────────────────────────────────────────────────


@router.post("/create_faces", response_model=UploadResponse)
async def create_faces(
    s3: S3Dep, payload: CreateFacesRequest
) -> UploadResponse:
    """Create (enroll) a baseline face-embedding vector.

    Stores under ``/enrollments/{username}/{device_id}.json``.
    """
    s3_key = f"enrollments/{payload.username}/{payload.device_id}.json"
    data = {
        "username": payload.username,
        "embedding": payload.embedding,
        "device_id": payload.device_id,
    }
    try:
        put_json(s3, s3_key, data)
    except Exception as exc:
        logger.exception("Failed to store face to S3")
        raise HTTPException(
            status_code=502, detail=f"S3 write failed: {exc}"
        ) from exc

    return UploadResponse(s3_key=s3_key, record_count=1)


@router.post("/get_faces", response_model=GetFacesResponse)
async def get_faces(s3: S3Dep, payload: GetFacesRequest) -> GetFacesResponse:
    """Retrieve enrolled face records for a given username.

    If ``device_id`` is provided, only that specific record is returned.
    Otherwise **all** face records for the user are returned.
    """
    if payload.device_id:
        keys = [f"enrollments/{payload.username}/{payload.device_id}.json"]
    else:
        prefix = f"enrollments/{payload.username}/"
        try:
            keys = list_keys(s3, prefix)
        except Exception as exc:
            logger.exception("Failed to list faces from S3")
            raise HTTPException(
                status_code=502, detail=f"S3 read failed: {exc}"
            ) from exc

    faces: list[FaceRecord] = []
    for key in keys:
        try:
            data = get_json(s3, key)
            if not isinstance(data, dict):
                logger.warning("Unexpected non-dict record: %s", key)
                continue

            faces.append(
                FaceRecord(
                    s3_key=key,
                    username=data["username"],
                    embedding=data["embedding"],
                    device_id=data["device_id"],
                )
            )
        except Exception:
            logger.warning("Skipping unreadable face record: %s", key)

    return GetFacesResponse(
        username=payload.username,
        faces=faces,
        count=len(faces),
    )


@router.post("/delete_faces", response_model=DeleteFacesResponse)
async def delete_faces(
    s3: S3Dep, payload: DeleteFacesRequest
) -> DeleteFacesResponse:
    """Delete enrolled face records for a user.

    If ``device_id`` is provided, only that specific record is deleted.
    Otherwise **all** face records for the user are removed.
    """
    if payload.device_id:
        # Delete a single specific face
        keys = [f"enrollments/{payload.username}/{payload.device_id}.json"]
    else:
        # Delete all faces for the user
        prefix = f"enrollments/{payload.username}/"
        try:
            keys = list_keys(s3, prefix)
        except Exception as exc:
            logger.exception("Failed to list faces for deletion")
            raise HTTPException(
                status_code=502, detail=f"S3 read failed: {exc}"
            ) from exc

    if not keys:
        raise HTTPException(
            status_code=404,
            detail=f"No face records found for user '{payload.username}'",
        )

    try:
        deleted = delete_keys(s3, keys)
    except Exception as exc:
        logger.exception("Failed to delete faces from S3")
        raise HTTPException(
            status_code=502, detail=f"S3 delete failed: {exc}"
        ) from exc

    return DeleteFacesResponse(deleted_count=deleted)
