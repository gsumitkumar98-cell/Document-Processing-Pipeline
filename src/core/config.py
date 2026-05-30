from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    APP_NAME: str = "Document Processing Pipeline"

    LOG_LEVEL: str = "INFO"

    CHUNK_SIZE: int = 50

    MAX_RESULTS: int = 5

    DOCUMENT_PATH: str = "documents"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()