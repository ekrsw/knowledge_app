"""Test configuration and fixtures with improved session management."""

import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.db.base import Base
from app.core.config import Settings


# テスト用の設定を作成
@pytest.fixture(scope="session")
def test_settings():
    """テスト用の設定を返す"""
    return Settings(
        ENVIRONMENT="testing",
        USER_POSTGRES_HOST=os.getenv("USER_POSTGRES_HOST", "localhost"),
        USER_POSTGRES_PORT=os.getenv("USER_POSTGRES_PORT", "5432"),
        USER_POSTGRES_USER=os.getenv("USER_POSTGRES_USER", "my_user"),
        USER_POSTGRES_PASSWORD=os.getenv("USER_POSTGRES_PASSWORD", "password"),
        USER_POSTGRES_DB=os.getenv("USER_POSTGRES_DB", "my_database"),
        SQLALCHEMY_ECHO=False,  # テスト中はSQLログを抑制
        LOG_LEVEL="WARNING"  # テスト中はログレベルを上げる
    )


# テスト用のデータベースエンジン
@pytest_asyncio.fixture(scope="session")
async def test_engine(test_settings):
    """テスト用のデータベースエンジンを作成"""
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        echo=test_settings.SQLALCHEMY_ECHO,
        future=True,
        pool_pre_ping=True,  # 接続の健全性チェック
        pool_recycle=300,    # 接続の再利用間隔
        connect_args={
            "server_settings": {
                "client_encoding": "utf8"
            }
        }
    )
    
    # テスト開始前にテーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # テスト終了後にテーブルを削除
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


# テスト用のセッションファクトリ
@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_engine):
    """テスト用のセッションファクトリを作成（expire_on_commit=False）"""
    return sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,  # greenletエラーを防ぐ
        autocommit=False,
        autoflush=False,
    )


# クリーンなデータベースセッション（推奨）
@pytest_asyncio.fixture
async def clean_db_session(test_session_factory):
    """各テスト用のクリーンなデータベースセッション（改善版）"""
    async with test_session_factory() as session:
        # テスト前にテストデータをクリーンアップ
        await session.execute(text(
            "DELETE FROM users WHERE username LIKE 'test%' OR username LIKE 'another%' "
            "OR username LIKE 'group%' OR username LIKE 'optional%' OR username LIKE 'valid%'"
        ))
        await session.commit()
        
        try:
            yield session
            # テスト成功時はコミット
            await session.commit()
        except Exception:
            # エラー時はロールバック
            await session.rollback()
            raise
        finally:
            # テスト後にテストデータをクリーンアップ
            try:
                await session.execute(text(
                    "DELETE FROM users WHERE username LIKE 'test%' OR username LIKE 'another%' "
                    "OR username LIKE 'group%' OR username LIKE 'optional%' OR username LIKE 'valid%'"
                ))
                await session.commit()
            except Exception:
                await session.rollback()


# ロールバック用のデータベースセッション
@pytest_asyncio.fixture
async def rollback_db_session(test_session_factory):
    """各テスト用のロールバックセッション（データを永続化しない）"""
    async with test_session_factory() as session:
        # ネストしたトランザクションを作成
        transaction = await session.begin()
        try:
            yield session
        finally:
            # 常にロールバック
            await transaction.rollback()


# テスト用のシンプルなセッション（expire_on_commit対応）
@pytest_asyncio.fixture
async def simple_db_session(test_session_factory):
    """シンプルなセッション管理（明示的なコミット/ロールバック）"""
    async with test_session_factory() as session:
        yield session
        # セッション終了時は自動的にclose()される