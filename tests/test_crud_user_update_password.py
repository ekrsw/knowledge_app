"""Password update tests for user CRUD operations."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.crud.exceptions import (
    InvalidPasswordError,
    MissingRequiredFieldError,
)
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings
from app.core.security import verify_password


class TestUserCRUDUpdatePassword:
    """ユーザーパスワード更新操作テスト"""

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
                "username LIKE 'passwordtest%' OR email LIKE '%passwordtest%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.fixture
    def sample_user_data(self):
        """サンプルユーザーデータを提供する"""
        return UserCreate(
            username="passwordtest_user",
            email="passwordtest@example.com",
            password="oldpassword123",
            full_name="Password Test User",
            group=GroupEnum.CSC_1,
            is_active=True,
            is_admin=False,
            is_sv=False
        )

    @pytest.mark.asyncio
    async def test_update_password_success(self, sample_user_data: UserCreate):
        """正常なパスワード更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                original_hashed_password = created_user.hashed_password
                await session.commit()
                
                # パスワードを更新
                new_password = "newpassword456"
                updated_user = await user_crud.update_password(
                    session, user_id, sample_user_data.password, new_password
                )
                
                # セッション内で即座に属性にアクセス
                updated_hashed_password = updated_user.hashed_password
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_hashed_password != original_hashed_password
                assert verify_password(new_password, updated_hashed_password)
                assert not verify_password(sample_user_data.password, updated_hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_nonexistent_user(self):
        """存在しないユーザーのパスワード更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在しないUUID
                nonexistent_id = "00000000-0000-0000-0000-000000000000"
                
                # パスワード更新を試行
                result = await user_crud.update_password(
                    session, nonexistent_id, "oldpass", "newpass"
                )
                
                # 検証
                assert result is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_invalid_old_password(self, sample_user_data: UserCreate):
        """間違った現在のパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 間違った現在のパスワードで更新を試行
                with pytest.raises(InvalidPasswordError) as exc_info:
                    await user_crud.update_password(
                        session, user_id, "wrongpassword", "newpassword456"
                    )
                
                assert "Current password is incorrect" in str(exc_info.value)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_empty_old_password(self, sample_user_data: UserCreate):
        """空の現在のパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 空の現在のパスワードで更新を試行
                with pytest.raises(MissingRequiredFieldError) as exc_info:
                    await user_crud.update_password(
                        session, user_id, "", "newpassword456"
                    )
                
                assert exc_info.value.field_name == "old_password"
                assert "Old password is required" in str(exc_info.value)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_empty_new_password(self, sample_user_data: UserCreate):
        """空の新しいパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 空の新しいパスワードで更新を試行
                with pytest.raises(MissingRequiredFieldError) as exc_info:
                    await user_crud.update_password(
                        session, user_id, sample_user_data.password, ""
                    )
                
                assert exc_info.value.field_name == "new_password"
                assert "New password is required" in str(exc_info.value)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_whitespace_old_password(self, sample_user_data: UserCreate):
        """空白のみの現在のパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 空白のみの現在のパスワードで更新を試行
                with pytest.raises(MissingRequiredFieldError) as exc_info:
                    await user_crud.update_password(
                        session, user_id, "   ", "newpassword456"
                    )
                
                assert exc_info.value.field_name == "old_password"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_whitespace_new_password(self, sample_user_data: UserCreate):
        """空白のみの新しいパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 空白のみの新しいパスワードで更新を試行
                with pytest.raises(MissingRequiredFieldError) as exc_info:
                    await user_crud.update_password(
                        session, user_id, sample_user_data.password, "   "
                    )
                
                assert exc_info.value.field_name == "new_password"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_same_password(self, sample_user_data: UserCreate):
        """同じパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                original_hashed_password = created_user.hashed_password
                await session.commit()
                
                # 同じパスワードで更新
                updated_user = await user_crud.update_password(
                    session, user_id, sample_user_data.password, sample_user_data.password
                )
                
                # セッション内で即座に属性にアクセス
                updated_hashed_password = updated_user.hashed_password
                
                await session.commit()
                
                # 検証（ハッシュは異なるが、両方とも同じパスワードを検証できる）
                assert updated_user is not None
                assert updated_hashed_password != original_hashed_password  # 新しいハッシュが生成される
                assert verify_password(sample_user_data.password, updated_hashed_password)
                assert verify_password(sample_user_data.password, original_hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_multiple_updates(self, sample_user_data: UserCreate):
        """複数回のパスワード更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 1回目のパスワード更新
                first_new_password = "firstnewpassword123"
                updated_user_1 = await user_crud.update_password(
                    session, user_id, sample_user_data.password, first_new_password
                )
                first_hashed_password = updated_user_1.hashed_password
                await session.commit()
                
                # 2回目のパスワード更新
                second_new_password = "secondnewpassword456"
                updated_user_2 = await user_crud.update_password(
                    session, user_id, first_new_password, second_new_password
                )
                second_hashed_password = updated_user_2.hashed_password
                await session.commit()
                
                # 検証
                assert updated_user_1 is not None
                assert updated_user_2 is not None
                assert first_hashed_password != second_hashed_password
                assert verify_password(first_new_password, first_hashed_password)
                assert verify_password(second_new_password, second_hashed_password)
                assert not verify_password(sample_user_data.password, second_hashed_password)
                assert not verify_password(first_new_password, second_hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_special_characters(self, sample_user_data: UserCreate):
        """特殊文字を含むパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 特殊文字を含むパスワードで更新
                special_password = "P@ssw0rd!@#$%^&*()_+-=[]{}|;:,.<>?"
                updated_user = await user_crud.update_password(
                    session, user_id, sample_user_data.password, special_password
                )
                
                # セッション内で即座に属性にアクセス
                updated_hashed_password = updated_user.hashed_password
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert verify_password(special_password, updated_hashed_password)
                assert not verify_password(sample_user_data.password, updated_hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_unicode_characters(self, sample_user_data: UserCreate):
        """Unicode文字を含むパスワードでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # Unicode文字を含むパスワードで更新
                unicode_password = "パスワード123測試😀"
                updated_user = await user_crud.update_password(
                    session, user_id, sample_user_data.password, unicode_password
                )
                
                # セッション内で即座に属性にアクセス
                updated_hashed_password = updated_user.hashed_password
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert verify_password(unicode_password, updated_hashed_password)
                assert not verify_password(sample_user_data.password, updated_hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)