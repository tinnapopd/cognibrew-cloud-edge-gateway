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


class EnrollmentRequest(BaseModel):
    """Initial enrollment of a baseline face vector."""

    username: str
    embedding: list[float] = Field(..., min_length=512, max_length=512)
    device_id: str = Field("manual", description="Source device or 'manual'")


class UploadResponse(BaseModel):
    """Standard success response after storing data."""

    status: str = "ok"
    s3_key: str = Field(..., description="Object key in S3")
    record_count: int = Field(0, description="Number of records stored")
