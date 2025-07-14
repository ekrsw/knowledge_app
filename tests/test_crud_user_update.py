"""Update operation tests for user CRUD operations."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.crud.exceptions import (
    DuplicateUsernameError,
    DuplicateEmailError,
)
from app.models.user import GroupEnum
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings


class TestUserCRUDUpdate:
    """ユーザー更新操作テスト"""

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
                "username LIKE 'updatetest%' OR email LIKE '%updatetest%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.fixture
    def sample_user_data(self):
        """サンプルユーザーデータを提供する"""
        return UserCreate(
            username="updatetest_user",
            email="updatetest@example.com",
            password="testpassword123",
            full_name="Update Test User",
            ctstage_name="Stage Name",
            sweet_name="Sweet Name",
            group=GroupEnum.CSC_1,
            is_active=True,
            is_admin=False,
            is_sv=False
        )

    @pytest.mark.asyncio
    async def test_update_user_basic_fields(self, sample_user_data: UserCreate):
        """基本フィールドの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 更新データを準備
                update_data = UserUpdate(
                    full_name="Updated Full Name",
                    ctstage_name="Updated Stage Name",
                    sweet_name="Updated Sweet Name"
                )
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_full_name = updated_user.full_name
                updated_ctstage_name = updated_user.ctstage_name
                updated_sweet_name = updated_user.sweet_name
                updated_username = updated_user.username
                updated_email = updated_user.email
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_full_name == "Updated Full Name"
                assert updated_ctstage_name == "Updated Stage Name"
                assert updated_sweet_name == "Updated Sweet Name"
                assert updated_username == sample_user_data.username  # 変更されていない
                assert updated_email == sample_user_data.email  # 変更されていない
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_username_and_email(self, sample_user_data: UserCreate):
        """ユーザー名とメールアドレスの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 更新データを準備
                update_data = UserUpdate(
                    username="updatetest_new_username",
                    email="new_updatetest@example.com"
                )
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_username = updated_user.username
                updated_email = updated_user.email
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_username == "updatetest_new_username"
                assert updated_email == "new_updatetest@example.com"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_group_and_permissions(self, sample_user_data: UserCreate):
        """グループと権限の更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 更新データを準備
                update_data = UserUpdate(
                    group=GroupEnum.HHD,
                    is_active=False,
                    is_admin=True,
                    is_sv=True
                )
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_group = updated_user.group
                updated_is_active = updated_user.is_active
                updated_is_admin = updated_user.is_admin
                updated_is_sv = updated_user.is_sv
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_group == GroupEnum.HHD
                assert updated_is_active == False
                assert updated_is_admin == True
                assert updated_is_sv == True
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_nonexistent_id(self):
        """存在しないIDでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在しないUUID
                nonexistent_id = "00000000-0000-0000-0000-000000000000"
                
                # 更新データを準備
                update_data = UserUpdate(
                    full_name="Should Not Update"
                )
                
                # 更新を試行
                result = await user_crud.update_user_by_id(session, nonexistent_id, update_data)
                
                # 検証
                assert result is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_empty_update_data(self, sample_user_data: UserCreate):
        """空の更新データでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                original_full_name = created_user.full_name
                await session.commit()
                
                # 空の更新データを準備
                update_data = UserUpdate()
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_full_name = updated_user.full_name
                
                await session.commit()
                
                # 検証（何も変更されていない）
                assert updated_user is not None
                assert updated_full_name == original_full_name
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_duplicate_username(self, sample_user_data: UserCreate):
        """重複ユーザー名での更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 最初のユーザーを作成
                first_user = await user_crud.create_user(session, sample_user_data)
                first_user_id = str(first_user.id)
                
                # 2番目のユーザーを作成
                second_user_data = UserCreate(
                    username="updatetest_second_user",
                    email="updatetest_second@example.com",
                    password="testpassword123",
                    group=GroupEnum.CSC_2
                )
                second_user = await user_crud.create_user(session, second_user_data)
                second_user_id = str(second_user.id)
                
                await session.commit()
                
                # 2番目のユーザーを1番目のユーザーと同じユーザー名に更新しようとする
                update_data = UserUpdate(
                    username=sample_user_data.username
                )
                
                # 重複エラーが発生することを確認
                with pytest.raises(DuplicateUsernameError):
                    await user_crud.update_user_by_id(session, second_user_id, update_data)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(self, sample_user_data: UserCreate):
        """重複メールアドレスでの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 最初のユーザーを作成
                first_user = await user_crud.create_user(session, sample_user_data)
                first_user_id = str(first_user.id)
                
                # 2番目のユーザーを作成
                second_user_data = UserCreate(
                    username="updatetest_second_user",
                    email="updatetest_second@example.com",
                    password="testpassword123",
                    group=GroupEnum.CSC_2
                )
                second_user = await user_crud.create_user(session, second_user_data)
                second_user_id = str(second_user.id)
                
                await session.commit()
                
                # 2番目のユーザーを1番目のユーザーと同じメールアドレスに更新しようとする
                update_data = UserUpdate(
                    email=sample_user_data.email
                )
                
                # 重複エラーが発生することを確認
                with pytest.raises(DuplicateEmailError):
                    await user_crud.update_user_by_id(session, second_user_id, update_data)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_same_username_and_email(self, sample_user_data: UserCreate):
        """同じユーザー名とメールアドレスでの更新テスト（自分自身は除外）"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # 同じユーザー名とメールアドレスで更新（自分自身なので問題なし）
                update_data = UserUpdate(
                    username=sample_user_data.username,
                    email=sample_user_data.email,
                    full_name="Updated Full Name"
                )
                
                # 更新が成功することを確認
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_username = updated_user.username
                updated_email = updated_user.email
                updated_full_name = updated_user.full_name
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_username == sample_user_data.username
                assert updated_email == sample_user_data.email
                assert updated_full_name == "Updated Full Name"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_partial_fields(self, sample_user_data: UserCreate):
        """一部フィールドのみの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                original_username = created_user.username
                original_email = created_user.email
                original_group = created_user.group
                await session.commit()
                
                # 一部のフィールドのみ更新
                update_data = UserUpdate(
                    full_name="Only Full Name Updated"
                )
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_username = updated_user.username
                updated_email = updated_user.email
                updated_full_name = updated_user.full_name
                updated_group = updated_user.group
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_full_name == "Only Full Name Updated"
                assert updated_username == original_username  # 変更されていない
                assert updated_email == original_email  # 変更されていない
                assert updated_group == original_group  # 変更されていない
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_all_optional_fields(self, sample_user_data: UserCreate):
        """すべてのオプションフィールドの更新テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # オプションフィールドなしでユーザーを作成
                minimal_user_data = UserCreate(
                    username="updatetest_minimal",
                    email="minimal@updatetest.com",
                    password="testpassword123",
                    group=GroupEnum.CSC_1
                )
                
                created_user = await user_crud.create_user(session, minimal_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # すべてのオプションフィールドを更新
                update_data = UserUpdate(
                    full_name="Added Full Name",
                    ctstage_name="Added Stage Name",
                    sweet_name="Added Sweet Name"
                )
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_full_name = updated_user.full_name
                updated_ctstage_name = updated_user.ctstage_name
                updated_sweet_name = updated_user.sweet_name
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_full_name == "Added Full Name"
                assert updated_ctstage_name == "Added Stage Name"
                assert updated_sweet_name == "Added Sweet Name"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_clear_optional_fields(self, sample_user_data: UserCreate):
        """オプションフィールドのクリアテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # フルデータでユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # オプションフィールドをクリア（Noneまたは空文字列）
                update_data = UserUpdate(
                    full_name=None,
                    ctstage_name=None,
                    sweet_name=None
                )
                
                # ユーザーを更新
                updated_user = await user_crud.update_user_by_id(session, user_id, update_data)
                
                # セッション内で即座に属性にアクセス
                updated_full_name = updated_user.full_name
                updated_ctstage_name = updated_user.ctstage_name
                updated_sweet_name = updated_user.sweet_name
                
                await session.commit()
                
                # 検証
                assert updated_user is not None
                assert updated_full_name is None
                assert updated_ctstage_name is None
                assert updated_sweet_name is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)