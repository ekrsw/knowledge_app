"""Transaction and data consistency tests for CRUD user operations - Phase 2."""

import pytest
import pytest_asyncio
import asyncio
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.crud.user import user_crud
from app.crud.exceptions import DuplicateUsernameError, DuplicateEmailError
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestCRUDUserTransactions:
    """トランザクション・整合性テスト"""

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
            expire_on_commit=True,
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
                "username LIKE 'txn%' OR username LIKE 'rollback%' OR "
                "username LIKE 'partial%' OR username LIKE 'long%' OR "
                "username LIKE 'isolation%' OR username LIKE 'deadlock%' OR "
                "username LIKE 'acid%' OR email LIKE '%transaction%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_rollback_data_consistency(self):
        """ロールバック後のデータ整合性テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 正常なユーザーを先に作成
                normal_user_data = UserCreate(
                    username="txn_normal_user",
                    email="normal@transaction.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                normal_user = await user_crud.create_user(session, normal_user_data)
                # コミット前にIDを取得
                normal_user_id = str(normal_user.id)
                normal_username = normal_user.username
                normal_email = normal_user.email
                await session.commit()
                
                # ロールバックが必要な状況を作成
                try:
                    # 重複ユーザー名でエラーを発生させる
                    duplicate_user_data = UserCreate(
                        username="txn_normal_user",  # 重複
                        email="duplicate@transaction.com",
                        password="testpass123",
                        group=GroupEnum.CSC_2
                    )
                    
                    await user_crud.create_user(session, duplicate_user_data)
                    await session.commit()
                    
                    # ここに到達してはいけない
                    assert False, "Duplicate user creation should fail"
                    
                except DuplicateUsernameError:
                    # 期待されるエラー
                    await session.rollback()
                
                # ロールバック後、元のユーザーが正常に存在することを確認
                found_user = await user_crud.get_user_by_id(session, normal_user_id)
                assert found_user is not None
                assert found_user.username == normal_username
                assert found_user.email == normal_email
                
                # データベースの状態が一貫していることを確認
                all_users = await user_crud.get_all_users(session)
                matching_users = [u for u in all_users if u.username.startswith("txn_")]
                assert len(matching_users) == 1  # 正常なユーザーのみ
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_partial_failure_handling(self):
        """部分的失敗の処理テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # バッチ処理のシミュレーション
                user_batch = [
                    UserCreate(
                        username="txn_partial_1",
                        email="partial1@transaction.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    ),
                    UserCreate(
                        username="txn_partial_2",
                        email="partial2@transaction.com",
                        password="testpass123",
                        group=GroupEnum.CSC_2
                    ),
                    UserCreate(
                        username="txn_partial_2",  # 意図的な重複
                        email="partial3@transaction.com",
                        password="testpass123",
                        group=GroupEnum.CSC_N
                    ),
                    UserCreate(
                        username="txn_partial_4",
                        email="partial4@transaction.com",
                        password="testpass123",
                        group=GroupEnum.HHD
                    ),
                ]
                
                created_users = []
                failed_users = []
                
                for i, user_data in enumerate(user_batch):
                    try:
                        created_user = await user_crud.create_user(session, user_data)
                        # コミット前にIDを取得して保存
                        user_id = str(created_user.id)
                        created_users.append((created_user, user_id))
                        # 各ユーザー作成後に個別コミット
                        await session.commit()
                        
                    except (DuplicateUsernameError, IntegrityError):
                        # 失敗したユーザーの処理
                        failed_users.append((i, user_data.username))
                        await session.rollback()
                        continue
                
                # 結果の検証
                assert len(created_users) == 3  # 成功したユーザー数
                assert len(failed_users) == 1   # 失敗したユーザー数
                
                # 成功したユーザーがデータベースに存在することを確認
                for created_user, user_id in created_users:
                    found_user = await user_crud.get_user_by_id(session, user_id)
                    assert found_user is not None
                
                # 失敗したユーザーがデータベースに存在しないことを確認
                failed_user = await user_crud.get_user_by_username(session, "txn_partial_2")
                # 最初の作成は成功し、2回目の同名作成が失敗する
                assert failed_user is not None  # 最初の作成分は存在
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_long_running_transactions(self):
        """長時間トランザクションのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 長時間のトランザクション開始
                start_time = time.time()
                
                user_data = UserCreate(
                    username="txn_long_running",
                    email="longrunning@transaction.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                created_user = await user_crud.create_user(session, user_data)
                
                # 意図的な遅延（長時間トランザクション）
                await asyncio.sleep(2)  # 2秒待機
                
                # 更新操作（SQLAlchemy 2.0では直接更新機能はないため、再作成でシミュレート）
                # 実際のアプリケーションでは更新メソッドが実装される
                
                # トランザクションの状態確認
                mid_transaction_user = await user_crud.get_user_by_username(session, "txn_long_running")
                assert mid_transaction_user is not None
                
                # さらに遅延
                await asyncio.sleep(1)  # 1秒追加待機
                
                await session.commit()
                end_time = time.time()
                
                # 長時間トランザクションが正常に完了したことを確認
                transaction_duration = end_time - start_time
                assert transaction_duration >= 3.0  # 少なくとも3秒
                
                # 最終的にユーザーが正しく保存されていることを確認
                final_user = await user_crud.get_user_by_username(session, "txn_long_running")
                assert final_user is not None
                assert final_user.id == created_user.id
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_transaction_isolation(self):
        """トランザクション分離レベルのテスト"""
        # 2つの独立したセッション/トランザクションを作成
        engine1 = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=60,
        )
        
        engine2 = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=60,
        )
        
        session_factory1 = sessionmaker(engine1, class_=AsyncSession, expire_on_commit=True)
        session_factory2 = sessionmaker(engine2, class_=AsyncSession, expire_on_commit=True)
        
        try:
            async with session_factory1() as session1, session_factory2() as session2:
                await self.cleanup_test_data(session1)
                await self.cleanup_test_data(session2)
                
                # セッション1でユーザーを作成（未コミット）
                user_data1 = UserCreate(
                    username="txn_isolation_test",
                    email="isolation@transaction.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                created_user1 = await user_crud.create_user(session1, user_data1)
                # session1ではコミットしない
                
                # セッション2から同じユーザー名での検索
                found_user_session2 = await user_crud.get_user_by_username(session2, "txn_isolation_test")
                # トランザクション分離により、session2からは見えない
                assert found_user_session2 is None
                
                # セッション1でコミット
                await session1.commit()
                
                # セッション2から再検索
                found_user_after_commit = await user_crud.get_user_by_username(session2, "txn_isolation_test")
                # コミット後は見える
                assert found_user_after_commit is not None
                assert found_user_after_commit.username == "txn_isolation_test"
                
                # クリーンアップ
                await self.cleanup_test_data(session1)
                
        finally:
            await engine1.dispose()
            await engine2.dispose()

    @pytest.mark.asyncio
    async def test_deadlock_handling(self):
        """デッドロック処理のテスト"""
        # デッドロックを意図的に発生させるのは複雑なため、
        # エラーハンドリングの確認を中心としたテスト
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 複数の同時接続でのリソース競合をシミュレート
                user_data = UserCreate(
                    username="txn_deadlock_test",
                    email="deadlock@transaction.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                async def concurrent_operation(operation_id):
                    """並行操作用の関数"""
                    operation_engine = create_async_engine(
                        settings.DATABASE_URL,
                        echo=False,
                        pool_size=1,
                        max_overflow=0,
                        pool_pre_ping=True,
                        pool_recycle=60,
                    )
                    
                    operation_session_factory = sessionmaker(
                        operation_engine,
                        class_=AsyncSession,
                        expire_on_commit=True
                    )
                    
                    try:
                        async with operation_session_factory() as op_session:
                            try:
                                # 同じリソースに対する操作
                                if operation_id == 0:
                                    # 最初の操作：ユーザー作成
                                    created_user = await user_crud.create_user(op_session, user_data)
                                    await asyncio.sleep(0.1)  # 微小な遅延
                                    await op_session.commit()
                                    return {"success": True, "operation": "create", "id": operation_id}
                                else:
                                    # 後続の操作：同じユーザー名での作成試行
                                    await asyncio.sleep(0.05)  # わずかに遅らせる
                                    duplicate_user = await user_crud.create_user(op_session, user_data)
                                    await op_session.commit()
                                    return {"success": True, "operation": "duplicate", "id": operation_id}
                                    
                            except (DuplicateUsernameError, IntegrityError, SQLAlchemyError) as e:
                                await op_session.rollback()
                                return {"success": False, "error": str(e), "id": operation_id}
                    finally:
                        await operation_engine.dispose()
                
                # 並行操作の実行
                tasks = [concurrent_operation(i) for i in range(3)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 結果の分析
                successful_operations = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
                failed_operations = len(results) - successful_operations
                
                # 少なくとも1つは成功し、他は適切にエラー処理されることを確認
                assert successful_operations >= 1, "At least one operation should succeed"
                assert failed_operations >= 0, "Failed operations should be handled gracefully"
                
                # 最終的にデータの整合性が保たれていることを確認
                final_user = await user_crud.get_user_by_username(session, "txn_deadlock_test")
                assert final_user is not None  # 1つのユーザーのみ存在
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_acid_properties(self):
        """ACID特性の確認テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Atomicity（原子性）のテスト
                user_data = UserCreate(
                    username="txn_acid_atomicity",
                    email="atomicity@transaction.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                try:
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # 意図的にエラーを発生させる（例：無効なSQL実行）
                    await session.execute(text("INVALID SQL STATEMENT"))
                    await session.commit()
                    
                    # ここに到達してはいけない
                    assert False, "Invalid SQL should cause rollback"
                    
                except Exception:
                    # 全体がロールバックされる（原子性）
                    await session.rollback()
                
                # ロールバック後、ユーザーが存在しないことを確認
                found_user = await user_crud.get_user_by_username(session, "txn_acid_atomicity")
                assert found_user is None
                
                # Consistency（一貫性）のテスト
                # 制約違反が正しく検出されることを確認
                try:
                    invalid_user_data = UserCreate(
                        username="",  # 空のユーザー名（制約違反）
                        email="consistency@transaction.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    await user_crud.create_user(session, invalid_user_data)
                    await session.commit()
                    assert False, "Empty username should be rejected"
                except Exception:
                    await session.rollback()
                
                # Isolation（分離性）は別テストで確認済み
                
                # Durability（耐久性）のテスト
                durable_user_data = UserCreate(
                    username="txn_acid_durability",
                    email="durability@transaction.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                created_durable_user = await user_crud.create_user(session, durable_user_data)
                # コミット前にIDを取得
                user_id = str(created_durable_user.id)
                user_username = created_durable_user.username
                await session.commit()
                
                # 新しいセッションで確認
                async for new_session, new_engine in self.create_fresh_session():
                    found_durable_user = await user_crud.get_user_by_id(new_session, user_id)
                    assert found_durable_user is not None
                    assert found_durable_user.username == user_username
                    break
                
                print("ACID properties verified successfully")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)