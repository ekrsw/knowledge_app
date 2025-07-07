import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional, Literal


class Settings(BaseSettings):
    # データベース関係
    USER_POSTGRES_HOST: str
    USER_POSTGRES_PORT: str
    USER_POSTGRES_USER: str
    USER_POSTGRES_PASSWORD: str
    USER_POSTGRES_DB: str
    TZ: str = "Asia/Tokyo"


    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.USER_POSTGRES_USER}:{self.USER_POSTGRES_PASSWORD}@"
            f"{self.USER_POSTGRES_HOST}:{self.USER_POSTGRES_PORT}/"
            f"{self.USER_POSTGRES_DB}"
        )
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        )



settings = Settings()