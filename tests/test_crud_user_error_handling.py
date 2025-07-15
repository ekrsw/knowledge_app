"""Error handling coverage tests for CRUD operations."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.crud.exceptions import (
    DatabaseIntegrityError,
    DuplicateEmailError,
)
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestUserCRUDErrorHandling:
    """エラーハンドリングのカバレッジ向上テスト"""

    async def create_fresh_session(self):
        """毎回新しいエンジンとセッションを作成"""
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=60,
        )
        
        session_factory = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        try:
            async with session_factory() as session:
                yield session, engine
        finally:
            await engine.dispose()

    async def cleanup_test_data(self, session):
        """テストデータをクリーンアップ"""
        try:
            await session.execute(text(
                "DELETE FROM users WHERE "
                "username LIKE 'errortest%' OR username LIKE 'exception%' OR "
                "email LIKE '%errortest%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_duplicate_email_error_handling(self):
        """重複メールエラーハンドリングのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 最初のユーザーを作成
                first_user_data = UserCreate(
                    username="errortest1",
                    email="errortest@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                first_user = await user_crud.create_user(session, first_user_data)
                await session.commit()
                
                # 重複メールで別のユーザーを作成しようとする
                duplicate_data = UserCreate(
                    username="errortest2",
                    email="errortest@example.com",  # 同じメール
                    password="testpass456",
                    group=GroupEnum.CSC_2
                )
                
                # DuplicateEmailErrorがスローされることを確認
                with pytest.raises(DuplicateEmailError) as exc_info:
                    await user_crud.create_user(session, duplicate_data)
                
                assert "Email already exists" in str(exc_info.value)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio 
    async def test_get_user_by_username_not_found(self):
        """存在しないユーザー名での検索テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在しないユーザー名で検索
                result = await user_crud.get_user_by_username(session, "nonexistent_user_12345")
                assert result is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """存在しないメールでの検索テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在しないメールで検索
                result = await user_crud.get_user_by_email(session, "nonexistent@example.com")
                assert result is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """存在しないIDでの検索テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在しないUUIDで検索
                import uuid
                fake_id = str(uuid.uuid4())
                result = await user_crud.get_user_by_id(session, fake_id)
                assert result is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_all_users_empty_result(self):
        """ユーザーが存在しない場合の全取得テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 全ユーザーを取得（空のリストが返される）
                all_users = await user_crud.get_all_users(session)
                
                # テストユーザーがいないことを確認
                test_users = [user for user in all_users if 'errortest' in user.username]
                assert len(test_users) == 0
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_create_user_database_error_simulation(self):
        """データベースエラー時の処理テスト（モック使用）"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                user_data = UserCreate(
                    username="exceptiontest",
                    email="exception@example.com", 
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                # session.commitをモックしてSQLAlchemyErrorをシミュレート
                with patch.object(session, 'commit', side_effect=SQLAlchemyError("Simulated DB error")):
                    with pytest.raises(DatabaseIntegrityError) as exc_info:
                        await user_crud.create_user(session, user_data)
                    
                    assert "Failed to create user" in str(exc_info.value)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_user_by_username_database_error(self):
        """get_user_by_username のデータベースエラーテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # session.executeをモックしてエラーをシミュレート
                with patch.object(session, 'execute', side_effect=SQLAlchemyError("DB connection error")):
                    with pytest.raises(SQLAlchemyError):
                        await user_crud.get_user_by_username(session, "testuser")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_user_by_email_database_error(self):
        """get_user_by_email のデータベースエラーテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # session.executeをモックしてエラーをシミュレート
                with patch.object(session, 'execute', side_effect=SQLAlchemyError("DB connection error")):
                    with pytest.raises(SQLAlchemyError):
                        await user_crud.get_user_by_email(session, "test@example.com")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_user_by_id_database_error(self):
        """get_user_by_id のデータベースエラーテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                import uuid
                test_id = str(uuid.uuid4())
                
                # session.executeをモックしてエラーをシミュレート
                with patch.object(session, 'execute', side_effect=SQLAlchemyError("DB connection error")):
                    with pytest.raises(SQLAlchemyError):
                        await user_crud.get_user_by_id(session, test_id)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_all_users_database_error(self):
        """get_all_users のデータベースエラーテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # session.executeをモックしてエラーをシミュレート
                with patch.object(session, 'execute', side_effect=SQLAlchemyError("DB connection error")):
                    with pytest.raises(SQLAlchemyError):
                        await user_crud.get_all_users(session)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)