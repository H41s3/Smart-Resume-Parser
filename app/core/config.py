"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Smart Resume Parser"
    app_version: str = "1.0.0"
    debug: bool = False

    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set[str] = {".pdf"}

    # NLP settings
    spacy_model: str = "en_core_web_sm"

    class Config:
        env_file = ".env"


settings = Settings()
