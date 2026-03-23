from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=False,
        env_ignore_empty=True,
        case_sensitive=False,
    )
    API_PREFIX_STR: str = "/api/v1"
    PROJECT_NAME: str = "CogniBrew Edge Gateway"
    ENVIRONMENT: Literal["local", "staging", "production"] = "production"

    # S3 / RustFS settings
    S3_ENDPOINT_URL: str = "http://rustfs:9000"
    S3_ACCESS_KEY: str = "rustfsadmin"
    S3_SECRET_KEY: str = "rustfsadmin"
    S3_BUCKET_NAME: str = "cognibrew-raw"


settings = Settings()  # type: ignore

