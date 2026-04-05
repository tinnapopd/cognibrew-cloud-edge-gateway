from pydantic import BaseModel, Field


class VectorRecord(BaseModel):
    username: str = Field(..., description="The user identity label")
    embedding: list[float] = Field(
        ...,
        min_length=512,
        max_length=512,
        description="512-dim face embedding",
    )
    is_correct: bool = Field(
        True, description="Edge feedback: was the recognition correct?"
    )


class BatchUpload(BaseModel):
    """Daily batch payload sent from an Edge device."""

    device_id: str = Field(..., description="Unique edge device identifier")
    date: str = Field(
        ...,
        description="ISO-8601 date string (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    vectors: list[VectorRecord] = Field(
        ..., min_length=1, description="Batch of face-embedding records"
    )


class CreateFacesRequest(BaseModel):
    """Request to create (enroll) a baseline face vector."""

    username: str
    embedding: list[float] = Field(..., min_length=512, max_length=512)
    device_id: str = Field(..., description="Source device")


class GetFacesRequest(BaseModel):
    """Request to retrieve enrolled face records."""

    username: str = Field(..., description="Username whose faces to retrieve")
    device_id: str = Field(
        ...,
        description="Specific device_id to retrieve faces for.",
    )


class DeleteFacesRequest(BaseModel):
    """Request to delete enrolled face records."""

    username: str = Field(..., description="Username whose faces to delete")
    device_id: str = Field(
        ...,
        description="Specific device_id to delete faces for.",
    )
    s3_key: str | None = Field(
        None,
        description="Specific S3 key of the face to delete.",
    )


class UploadResponse(BaseModel):
    """Standard success response after storing data."""

    status: str = "ok"
    s3_key: str = Field(..., description="Object key in S3")
    record_count: int = Field(0, description="Number of records stored")


class FaceRecord(BaseModel):
    """A single enrolled face record."""

    s3_key: str
    username: str
    embedding: list[float]
    device_id: str


class GetFacesResponse(BaseModel):
    """Response for the get_faces endpoint."""

    status: str = "ok"
    username: str
    faces: list[FaceRecord] = Field(default_factory=list)
    count: int = 0


class DeleteFacesResponse(BaseModel):
    """Response for the delete_faces endpoint."""

    status: str = "ok"
    deleted_count: int = 0
