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

    # Redis設定
    AUTH_REDIS_HOST: str = "auth_redis"
    AUTH_REDIS_PORT: str = "6379"
    AUTH_REDIS_USER: str = "admin"
    AUTH_REDIS_PASSWORD: str = "my_password"

    # トークン設定
    ALGORITHM: str = "RS256"
    PRIVATE_KEY_PATH: str = "keys/private.pem"  # 秘密鍵のパス
    PUBLIC_KEY_PATH: str = "keys/public.pem"   # 公開鍵のパス
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # トークンブラックリスト関連の設定
    TOKEN_BLACKLIST_ENABLED: bool = True


    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.USER_POSTGRES_USER}:{self.USER_POSTGRES_PASSWORD}@"
            f"{self.USER_POSTGRES_HOST}:{self.USER_POSTGRES_PORT}/"
            f"{self.USER_POSTGRES_DB}"
        )
    
    @property
    def AUTH_REDIS_URL(self) -> str:
        return f"redis://{self.AUTH_REDIS_USER}:{self.AUTH_REDIS_PASSWORD}@{self.AUTH_REDIS_HOST}:{self.AUTH_REDIS_PORT}/0"
    
    @property
    def PRIVATE_KEY(self) -> str:
        """秘密鍵の内容を読み込む"""
        try:
            with open(self.PRIVATE_KEY_PATH, "r") as f:
                return f.read()
        except FileNotFoundError:
            # 開発環境では環境変数から直接読み込む選択肢も
            return os.environ.get("PRIVATE_KEY", "")
    
    @property
    def PUBLIC_KEY(self) -> str:
        """公開鍵の内容を読み込む"""
        try:
            with open(self.PUBLIC_KEY_PATH, "r") as f:
                return f.read()
        except FileNotFoundError:
            return os.environ.get("PUBLIC_KEY", "")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        )



settings = Settings()