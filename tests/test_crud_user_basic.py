"""Basic CRUD tests for user operations."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.crud.exceptions import (
    DuplicateUsernameError,
    MissingRequiredFieldError,
)
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestUserCRUDBasic:
    """基本的なCRUD操作テスト"""

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
                "username LIKE 'basictest%' OR username LIKE 'duplicatetest%' OR "
                "username LIKE 'alltest%' OR email LIKE '%basictest%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.fixture
    def sample_user_data(self):
        """サンプルユーザーデータを提供する"""
        return UserCreate(
            username="basictest_user",
            email="basictest@example.com",
            password="testpassword123",
            full_name="Basic Test User",
            group=GroupEnum.CSC_1,
            is_active=True,
            is_admin=False,
            is_sv=False
        )

    @pytest.mark.asyncio
    async def test_create_user_success(self, sample_user_data: UserCreate):
        """正常なユーザー作成テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                
                # セッション内で即座に属性にアクセス
                user_id = created_user.id
                username = created_user.username
                email = created_user.email
                full_name = created_user.full_name
                group = created_user.group
                hashed_password = created_user.hashed_password
                
                await session.commit()
                
                # 検証
                assert created_user is not None
                assert username == sample_user_data.username
                assert email == sample_user_data.email
                assert full_name == sample_user_data.full_name
                assert group == sample_user_data.group
                assert hashed_password != sample_user_data.password
                assert len(hashed_password) > 0
                assert user_id is not None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_missing_username(self, sample_user_data: UserCreate):
        """ユーザー名不足テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                sample_user_data.username = ""
                
                with pytest.raises(MissingRequiredFieldError) as exc_info:
                    await user_crud.create_user(session, sample_user_data)
                
                assert exc_info.value.field_name == "username"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_duplicate_username(self, sample_user_data: UserCreate):
        """重複ユーザー名テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 最初のユーザーを作成
                first_user = await user_crud.create_user(session, sample_user_data)
                first_user_id = first_user.id
                await session.commit()
                
                # 重複ユーザーを作成しようとする
                duplicate_data = UserCreate(
                    username=sample_user_data.username,
                    email="different@basictest.com",
                    password="differentpass",
                    group=GroupEnum.CSC_2
                )
                
                with pytest.raises(DuplicateUsernameError):
                    await user_crud.create_user(session, duplicate_data)
                
                # 元のユーザーが存在することを確認
                existing = await user_crud.get_user_by_username(session, sample_user_data.username)
                assert existing is not None
                assert existing.id == first_user_id
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_operations(self, sample_user_data: UserCreate):
        """取得操作テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザー作成
                created_user = await user_crud.create_user(session, sample_user_data)
                created_user_id = str(created_user.id)
                await session.commit()
                
                # 各種検索テスト
                found_by_username = await user_crud.get_user_by_username(session, sample_user_data.username)
                assert found_by_username is not None
                assert found_by_username.username == sample_user_data.username
                
                found_by_email = await user_crud.get_user_by_email(session, sample_user_data.email)
                assert found_by_email is not None
                assert found_by_email.email == sample_user_data.email
                
                found_by_id = await user_crud.get_user_by_id(session, created_user_id)
                assert found_by_id is not None
                assert str(found_by_id.id) == created_user_id
                
                # 存在しない検索
                not_found = await user_crud.get_user_by_username(session, "nonexistent")
                assert not_found is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_get_all_users(self):
        """全ユーザー取得テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 複数のユーザーを作成
                users_data = [
                    UserCreate(username="alltest1", email="all1@basictest.com", password="pass123", group=GroupEnum.CSC_1),
                    UserCreate(username="alltest2", email="all2@basictest.com", password="pass123", group=GroupEnum.CSC_2),
                    UserCreate(username="alltest3", email="all3@basictest.com", password="pass123", group=GroupEnum.HHD)
                ]
                
                created_users = []
                for user_data in users_data:
                    created_user = await user_crud.create_user(session, user_data)
                    created_users.append(created_user)
                
                await session.commit()
                
                # 全ユーザーを取得
                all_users = await user_crud.get_all_users(session)
                
                # テストユーザーをフィルタ
                test_users = [user for user in all_users if user.username.startswith("alltest")]
                assert len(test_users) == 3
                
                # 作成したユーザーが含まれていることを確認
                usernames = {user.username for user in test_users}
                assert "alltest1" in usernames
                assert "alltest2" in usernames
                assert "alltest3" in usernames
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_username_whitespace_validation(self):
        """ユーザー名空白バリデーションテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザー名が空白のみの場合のテスト（最小長制約をクリア）
                user_data = UserCreate(
                    username="   ",  # 3文字の空白
                    email="whitespace@basictest.com",
                    password="validpass123",
                    group=GroupEnum.CSC_1
                )
                
                with pytest.raises(MissingRequiredFieldError) as exc_info:
                    await user_crud.create_user(session, user_data)
                
                assert exc_info.value.field_name == "username"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)