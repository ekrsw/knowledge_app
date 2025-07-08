import os
from tokenize import triple_quoted
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional, Literal


class Settings(BaseSettings):
    # 環境設定
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    
    # ロギング設定
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/api_server.log"

    # データベース関係
    USER_POSTGRES_HOST: str
    USER_POSTGRES_PORT: str
    USER_POSTGRES_USER: str
    USER_POSTGRES_PASSWORD: str
    USER_POSTGRES_DB: str
    TZ: str = "Asia/Tokyo"

    # SQLAlchemyのログ出力設定
    SQLALCHEMY_ECHO: bool = True

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
        env_prefix="",
        case_sensitive=False,
        )



settings = Settings()