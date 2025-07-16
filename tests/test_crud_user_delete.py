"""Delete operation tests for user CRUD operations."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.crud.exceptions import UserNotFoundError
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestUserCRUDDelete:
    """ユーザー削除操作テスト"""

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
                "username LIKE 'deletetest%' OR email LIKE '%deletetest%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.fixture
    def sample_user_data(self):
        """サンプルユーザーデータを提供する"""
        return UserCreate(
            username="deletetest_user",
            email="deletetest@example.com",
            password="testpassword123",
            full_name="Delete Test User",
            ctstage_name="Stage Name",
            sweet_name="Sweet Name",
            group=GroupEnum.CSC_1,
            is_active=True,
            is_admin=False,
            is_sv=False
        )

    @pytest.mark.asyncio
    async def test_delete_user_success(self, sample_user_data: UserCreate):
        """正常なユーザー削除テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザーを作成
                created_user = await user_crud.create_user(session, sample_user_data)
                user_id = str(created_user.id)
                created_username = created_user.username
                await session.commit()
                
                # ユーザーが存在することを確認
                existing_user = await user_crud.get_user_by_id(session, user_id)
                assert existing_user is not None
                
                # ユーザーを削除
                deleted_user = await user_crud.delete_user_by_id(session, user_id)
                
                # セッション内で即座に属性にアクセス
                deleted_username = deleted_user.username
                deleted_user_id = str(deleted_user.id)
                
                await session.commit()
                
                # 検証
                assert deleted_user is not None
                assert deleted_username == created_username
                assert deleted_user_id == user_id
                
                # 削除後にユーザーが存在しないことを確認
                non_existing_user = await user_crud.get_user_by_id(session, user_id)
                assert non_existing_user is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_delete_user_nonexistent_id(self):
        """存在しないIDでの削除テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在しないUUID
                nonexistent_id = "00000000-0000-0000-0000-000000000000"
                
                # UserNotFoundErrorが発生することを確認
                with pytest.raises(UserNotFoundError) as exc_info:
                    await user_crud.delete_user_by_id(session, nonexistent_id)
                
                # エラーメッセージの検証（セキュリティ強化: 汎用的なメッセージ）
                assert str(exc_info.value) == "User not found"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_delete_user_multiple_operations(self, sample_user_data: UserCreate):
        """複数ユーザーの削除テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 複数のユーザーを作成
                user1_data = sample_user_data
                user2_data = UserCreate(
                    username="deletetest_user2",
                    email="deletetest2@example.com",
                    password="testpassword123",
                    group=GroupEnum.CSC_2
                )
                
                created_user1 = await user_crud.create_user(session, user1_data)
                created_user2 = await user_crud.create_user(session, user2_data)
                user1_id = str(created_user1.id)
                user2_id = str(created_user2.id)
                
                await session.commit()
                
                # 両方のユーザーが存在することを確認
                existing_user1 = await user_crud.get_user_by_id(session, user1_id)
                existing_user2 = await user_crud.get_user_by_id(session, user2_id)
                assert existing_user1 is not None
                assert existing_user2 is not None
                
                # 最初のユーザーを削除
                deleted_user1 = await user_crud.delete_user_by_id(session, user1_id)
                await session.commit()
                
                # 1番目のユーザーが削除され、2番目のユーザーが存在することを確認
                non_existing_user1 = await user_crud.get_user_by_id(session, user1_id)
                still_existing_user2 = await user_crud.get_user_by_id(session, user2_id)
                assert non_existing_user1 is None
                assert still_existing_user2 is not None
                
                # 2番目のユーザーも削除
                deleted_user2 = await user_crud.delete_user_by_id(session, user2_id)
                await session.commit()
                
                # 両方のユーザーが削除されたことを確認
                non_existing_user1_final = await user_crud.get_user_by_id(session, user1_id)
                non_existing_user2_final = await user_crud.get_user_by_id(session, user2_id)
                assert non_existing_user1_final is None
                assert non_existing_user2_final is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_delete_user_with_all_fields(self):
        """すべてのフィールドを持つユーザーの削除テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # フルデータでユーザーを作成
                full_user_data = UserCreate(
                    username="deletetest_full_user",
                    email="deletefull@test.com",
                    password="testpassword123",
                    full_name="Full Name User",
                    ctstage_name="Full Stage Name",
                    sweet_name="Full Sweet Name",
                    group=GroupEnum.HHD,
                    is_active=True,
                    is_admin=True,
                    is_sv=True
                )
                
                created_user = await user_crud.create_user(session, full_user_data)
                user_id = str(created_user.id)
                await session.commit()
                
                # ユーザーを削除
                deleted_user = await user_crud.delete_user_by_id(session, user_id)
                
                # セッション内で属性を取得
                deleted_full_name = deleted_user.full_name
                deleted_group = deleted_user.group
                deleted_is_admin = deleted_user.is_admin
                
                await session.commit()
                
                # 検証
                assert deleted_user is not None
                assert deleted_full_name == "Full Name User"
                assert deleted_group == GroupEnum.HHD
                assert deleted_is_admin == True
                
                # 削除後に存在しないことを確認
                non_existing_user = await user_crud.get_user_by_id(session, user_id)
                assert non_existing_user is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)