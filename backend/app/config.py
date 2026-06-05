import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AETHERIX"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./aetherix.db"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
