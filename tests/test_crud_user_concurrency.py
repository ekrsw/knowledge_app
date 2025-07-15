"""Concurrency and TOCTOU (Time-of-Check-Time-of-Use) tests for CRUD user operations."""

import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.crud.exceptions import DuplicateUsernameError, DuplicateEmailError
from app.models.user import GroupEnum
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings


class TestCRUDUserConcurrency:
    """並行性とTOCTOU対策テスト"""

    async def create_fresh_session(self):
        """毎回新しいエンジンとセッションを作成"""
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=5,  # 並行テスト用に増加
            max_overflow=10,
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
                "username LIKE 'concurrent%' OR username LIKE 'race%' OR username LIKE 'stress_test_user_%' OR "
                "email LIKE 'concurrent%' OR email LIKE 'race%' OR email LIKE 'stress_test%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    async def create_user_task(self, user_data):
        """独立したセッションでユーザー作成タスクを実行"""
        async for session, engine in self.create_fresh_session():
            try:
                return await user_crud.create_user(session, user_data)
            except Exception as e:
                return e
            finally:
                pass  # セッションは自動的に閉じられる

    async def update_user_task(self, user_id, update_data):
        """独立したセッションでユーザー更新タスクを実行"""
        async for session, engine in self.create_fresh_session():
            try:
                return await user_crud.update_user_by_id(session, user_id, update_data)
            except Exception as e:
                return e
            finally:
                pass  # セッションは自動的に閉じられる

    @pytest.mark.asyncio
    async def test_concurrent_user_creation_duplicate_username(self):
        """並行でのユーザー作成時の重複ユーザー名処理テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)

                # 同じユーザー名で同時に作成を試行
                user_data1 = UserCreate(
                    username="concurrent_user_test",
                    email="concurrent1@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                user_data2 = UserCreate(
                    username="concurrent_user_test",  # 同じユーザー名
                    email="concurrent2@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )

                # 並行実行（独立したセッションで）
                results = await asyncio.gather(
                    self.create_user_task(user_data1),
                    self.create_user_task(user_data2),
                    return_exceptions=True
                )

                # 結果の検証
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                duplicate_errors = sum(1 for r in results if isinstance(r, DuplicateUsernameError))

                assert success_count == 1, "Only one user should be created successfully"
                assert duplicate_errors == 1, "One duplicate username error should occur"

            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_concurrent_user_creation_duplicate_email(self):
        """並行でのユーザー作成時の重複メールアドレス処理テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)

                # 同じメールアドレスで同時に作成を試行
                user_data1 = UserCreate(
                    username="concurrent_user1",
                    email="concurrent@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                user_data2 = UserCreate(
                    username="concurrent_user2",
                    email="concurrent@example.com",  # 同じメールアドレス
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )

                # 並行実行（独立したセッションで）
                results = await asyncio.gather(
                    self.create_user_task(user_data1),
                    self.create_user_task(user_data2),
                    return_exceptions=True
                )

                # 結果の検証
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                duplicate_errors = sum(1 for r in results if isinstance(r, DuplicateEmailError))

                assert success_count == 1, "Only one user should be created successfully"
                assert duplicate_errors == 1, "One duplicate email error should occur"

            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_concurrent_user_update_duplicate_username(self):
        """並行でのユーザー更新時の重複ユーザー名処理テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)

                # 事前に3つのユーザーを作成
                user_data1 = UserCreate(
                    username="race_user1",
                    email="race1@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                user_data2 = UserCreate(
                    username="race_user2",
                    email="race2@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                target_user_data = UserCreate(
                    username="race_target",
                    email="race_target@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )

                created_user1 = await user_crud.create_user(session, user_data1)
                created_user2 = await user_crud.create_user(session, user_data2)
                target_user = await user_crud.create_user(session, target_user_data)

                # 2つのユーザーを同じユーザー名に更新しようとする
                update_data = UserUpdate(username="race_target_updated")

                # 並行実行（独立したセッションで）
                results = await asyncio.gather(
                    self.update_user_task(str(created_user1.id), update_data),
                    self.update_user_task(str(created_user2.id), update_data),
                    return_exceptions=True
                )

                # 結果の検証
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                duplicate_errors = sum(1 for r in results if isinstance(r, DuplicateUsernameError))

                assert success_count == 1, "Only one user should be updated successfully"
                assert duplicate_errors == 1, "One duplicate username error should occur"

            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_concurrent_user_update_duplicate_email(self):
        """並行でのユーザー更新時の重複メールアドレス処理テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)

                # 事前に3つのユーザーを作成
                user_data1 = UserCreate(
                    username="race_email_user1",
                    email="race_email1@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                user_data2 = UserCreate(
                    username="race_email_user2",
                    email="race_email2@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                target_user_data = UserCreate(
                    username="race_email_target",
                    email="race_email_target@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )

                created_user1 = await user_crud.create_user(session, user_data1)
                created_user2 = await user_crud.create_user(session, user_data2)
                target_user = await user_crud.create_user(session, target_user_data)

                # 2つのユーザーを同じメールアドレスに更新しようとする
                update_data = UserUpdate(email="race_email_updated@example.com")

                # 並行実行（独立したセッションで）
                results = await asyncio.gather(
                    self.update_user_task(str(created_user1.id), update_data),
                    self.update_user_task(str(created_user2.id), update_data),
                    return_exceptions=True
                )

                # 結果の検証
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                duplicate_errors = sum(1 for r in results if isinstance(r, DuplicateEmailError))

                assert success_count == 1, "Only one user should be updated successfully"
                assert duplicate_errors == 1, "One duplicate email error should occur"

            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_race_condition_prevention(self):
        """TOCTOU レース条件が適切に防止されることを確認"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)

                # 多数の並行タスクで同じユーザー名での作成を試行
                user_data_list = [
                    UserCreate(
                        username="race_prevention_test",
                        email=f"race_prevention{i}@example.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    for i in range(10)
                ]

                # 並行実行（独立したセッションで）
                results = await asyncio.gather(
                    *[self.create_user_task(user_data) for user_data in user_data_list],
                    return_exceptions=True
                )

                # 結果の検証
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                duplicate_errors = sum(1 for r in results if isinstance(r, DuplicateUsernameError))

                assert success_count == 1, "Only one user should be created successfully"
                assert duplicate_errors == 9, "Nine duplicate username errors should occur"

                # 作成されたユーザーが存在することを確認
                created_user = await user_crud.get_user_by_username(session, "race_prevention_test")
                assert created_user is not None, "User should be created"

            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_high_concurrency_stress_test(self):
        """高い並行性でのストレステスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)

                # 大量の並行タスクを実行
                user_data_list = []
                for i in range(20):
                    user_data = UserCreate(
                        username=f"stress_test_user_{i}",
                        email=f"stress_test{i}@example.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    user_data_list.append(user_data)

                # 並行実行（独立したセッションで）
                results = await asyncio.gather(*[self.create_user_task(user_data) for user_data in user_data_list], return_exceptions=True)

                # 結果の検証
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                error_count = sum(1 for r in results if isinstance(r, Exception))

                # 全てのタスクが成功するはず（異なるユーザー名とメールアドレスを使用）
                assert success_count == 20, f"All 20 users should be created successfully, but got {success_count}"
                assert error_count == 0, f"No errors should occur, but got {error_count}"

                # 作成されたユーザー数を確認
                all_users = await user_crud.get_all_users(session)
                stress_users = [u for u in all_users if u.username.startswith("stress_test_user_")]
                assert len(stress_users) == 20, "All 20 users should be in the database"

            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)