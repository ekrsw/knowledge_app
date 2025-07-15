"""Integration and real-world scenario tests for CRUD user operations - Phase 2."""

import pytest
import pytest_asyncio
import asyncio
import time
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from app.crud.user import user_crud
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestCRUDUserIntegration:
    """統合・実用シナリオテスト"""

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
                "username LIKE 'integration%' OR username LIKE 'admin%' OR "
                "username LIKE 'workflow%' OR username LIKE 'migration%' OR "
                "username LIKE 'disaster%' OR username LIKE 'system%' OR "
                "email LIKE '%integration%' OR email LIKE '%workflow%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_user_registration_workflow(self):
        """ユーザー登録ワークフローのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # フェーズ1: 初期ユーザー登録
                registration_data = UserCreate(
                    username="integration_new_user",
                    email="newuser@integration.com",
                    password="temppass123",
                    group=GroupEnum.CSC_1,
                    full_name="新規登録ユーザー",
                    is_active=False,  # 初期は非アクティブ
                    is_admin=False,
                    is_sv=False
                )
                
                # ユーザー作成
                new_user = await user_crud.create_user(session, registration_data)
                assert new_user is not None
                assert new_user.is_active is False  # 初期状態確認
                
                # コミット前に必要なデータを取得
                user_id = str(new_user.id)
                user_username = new_user.username
                user_email = new_user.email
                user_group = new_user.group
                await session.commit()
                
                # フェーズ2: ユーザー情報検証
                created_user = await user_crud.get_user_by_username(session, user_username)
                assert created_user is not None
                assert str(created_user.id) == user_id
                assert created_user.email == user_email
                assert created_user.is_active is False
                
                # フェーズ3: メール検証シミュレーション（実際のアプリではメール確認）
                # 現在のCRUDには更新機能がないため、アクティベーション状態確認のみ
                email_verified_user = await user_crud.get_user_by_email(session, user_email)
                assert email_verified_user is not None
                assert str(email_verified_user.id) == user_id
                
                # フェーズ4: 完全なユーザープロファイル確認
                complete_user = await user_crud.get_user_by_id(session, user_id)
                assert complete_user is not None
                assert complete_user.username == user_username
                assert complete_user.full_name == "新規登録ユーザー"
                assert complete_user.group == user_group
                
                # フェーズ5: パスワード検証テスト
                from app.core.security import verify_password
                assert verify_password("temppass123", complete_user.hashed_password)
                assert not verify_password("wrongpassword", complete_user.hashed_password)
                
                print("User registration workflow completed successfully")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_admin_operations_workflow(self):
        """システム管理操作ワークフローのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # フェーズ1: システム管理者作成
                admin_data = UserCreate(
                    username="integration_admin",
                    email="admin@integration.com",
                    password="adminpass123",
                    group=GroupEnum.HHD,
                    full_name="システム管理者",
                    is_active=True,
                    is_admin=True,
                    is_sv=True
                )
                
                admin_user = await user_crud.create_user(session, admin_data)
                assert admin_user.is_admin is True
                assert admin_user.is_sv is True
                
                # 管理者情報を安全に保存
                admin_id = str(admin_user.id)
                admin_username = admin_user.username
                await session.commit()
                
                # フェーズ2: 一般ユーザー作成（管理者による操作）
                regular_users_data = [
                    UserCreate(
                        username=f"integration_user_{i}",
                        email=f"user{i}@integration.com",
                        password="userpass123",
                        group=GroupEnum.CSC_1 if i % 2 == 0 else GroupEnum.CSC_2,
                        full_name=f"一般ユーザー{i}",
                        is_active=True,
                        is_admin=False,
                        is_sv=False
                    )
                    for i in range(1, 6)  # 5人のユーザー
                ]
                
                created_regular_users = []
                for user_data in regular_users_data:
                    regular_user = await user_crud.create_user(session, user_data)
                    # 安全なデータ保存
                    user_info = {
                        'id': str(regular_user.id),
                        'username': regular_user.username,
                        'email': regular_user.email,
                        'group': regular_user.group,
                        'is_admin': regular_user.is_admin,
                        'is_sv': regular_user.is_sv
                    }
                    created_regular_users.append(user_info)
                    await session.commit()
                
                # フェーズ3: 全ユーザー取得（管理機能）
                all_users = await user_crud.get_all_users(session)
                integration_users = [u for u in all_users if u.username.startswith("integration_")]
                assert len(integration_users) == 6  # 管理者1 + 一般ユーザー5
                
                # フェーズ4: 権限レベル確認
                admin_users = [u for u in integration_users if u.is_admin]
                regular_users = [u for u in integration_users if not u.is_admin]
                sv_users = [u for u in integration_users if u.is_sv]
                
                assert len(admin_users) == 1
                assert len(regular_users) == 5
                assert len(sv_users) == 1  # 管理者のみSV権限
                
                # フェーズ5: グループ別ユーザー確認
                csc1_users = [u for u in integration_users if u.group == GroupEnum.CSC_1]
                csc2_users = [u for u in integration_users if u.group == GroupEnum.CSC_2]
                hhd_users = [u for u in integration_users if u.group == GroupEnum.HHD]
                
                assert len(csc1_users) >= 2  # 偶数番号のユーザー
                assert len(csc2_users) >= 2  # 奇数番号のユーザー
                assert len(hhd_users) == 1   # 管理者のみ
                
                # フェーズ6: 個別ユーザー検索
                for user_info in created_regular_users:
                    found_user = await user_crud.get_user_by_username(session, user_info['username'])
                    assert found_user is not None
                    assert str(found_user.id) == user_info['id']
                
                print("Admin operations workflow completed successfully")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_data_migration_scenarios(self):
        """データ移行シナリオのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # フェーズ1: 既存システムからのデータ移行シミュレーション
                legacy_users_data = [
                    {
                        "username": "integration_legacy_admin",
                        "email": "legacy.admin@integration.com",
                        "full_name": "レガシー管理者",
                        "group": GroupEnum.HHD,
                        "is_admin": True,
                        "is_active": True,
                        "is_sv": True
                    },
                    {
                        "username": "integration_legacy_dev1",
                        "email": "legacy.dev1@integration.com",
                        "full_name": "レガシー開発者1",
                        "group": GroupEnum.CSC_1,
                        "is_admin": False,
                        "is_active": True,
                        "is_sv": False
                    },
                    {
                        "username": "integration_legacy_dev2",
                        "email": "legacy.dev2@integration.com",
                        "full_name": "レガシー開発者2",
                        "group": GroupEnum.CSC_2,
                        "is_admin": False,
                        "is_active": False,  # 非アクティブユーザー
                        "is_sv": False
                    },
                    {
                        "username": "integration_legacy_sv",
                        "email": "legacy.sv@integration.com",
                        "full_name": "レガシーSV",
                        "group": GroupEnum.CSC_N,
                        "is_admin": False,
                        "is_active": True,
                        "is_sv": True
                    }
                ]
                
                # バッチでのユーザー移行
                migrated_users = []
                migration_errors = []
                
                for i, legacy_data in enumerate(legacy_users_data):
                    try:
                        user_create_data = UserCreate(
                            username=legacy_data["username"],
                            email=legacy_data["email"],
                            password="migrated123",  # 移行時の仮パスワード
                            group=legacy_data["group"],
                            full_name=legacy_data["full_name"],
                            is_active=legacy_data["is_active"],
                            is_admin=legacy_data["is_admin"],
                            is_sv=legacy_data["is_sv"]
                        )
                        
                        migrated_user = await user_crud.create_user(session, user_create_data)
                        
                        # 安全なデータ保存
                        user_info = {
                            'id': str(migrated_user.id),
                            'username': migrated_user.username,
                            'email': migrated_user.email,
                            'full_name': migrated_user.full_name,
                            'group': migrated_user.group,
                            'is_active': migrated_user.is_active,
                            'is_admin': migrated_user.is_admin,
                            'is_sv': migrated_user.is_sv
                        }
                        migrated_users.append(user_info)
                        await session.commit()
                        
                    except Exception as e:
                        migration_errors.append((i, str(e)))
                        await session.rollback()
                        continue
                
                # フェーズ2: 移行結果の検証
                assert len(migrated_users) == 4  # 全ユーザーが正常に移行
                assert len(migration_errors) == 0  # エラーなし
                
                # フェーズ3: 移行データの整合性確認
                for original_data, migrated_user in zip(legacy_users_data, migrated_users):
                    assert migrated_user['username'] == original_data["username"]
                    assert migrated_user['email'] == original_data["email"]
                    assert migrated_user['full_name'] == original_data["full_name"]
                    assert migrated_user['group'] == original_data["group"]
                    assert migrated_user['is_active'] == original_data["is_active"]
                    assert migrated_user['is_admin'] == original_data["is_admin"]
                    assert migrated_user['is_sv'] == original_data["is_sv"]
                
                # フェーズ4: 移行後の統計情報
                all_migrated = await user_crud.get_all_users(session)
                legacy_users = [u for u in all_migrated if u.username.startswith("integration_legacy_")]
                
                active_count = sum(1 for u in legacy_users if u.is_active)
                inactive_count = sum(1 for u in legacy_users if not u.is_active)
                admin_count = sum(1 for u in legacy_users if u.is_admin)
                sv_count = sum(1 for u in legacy_users if u.is_sv)
                
                assert active_count == 3
                assert inactive_count == 1
                assert admin_count == 1
                assert sv_count == 2  # admin + sv
                
                print("Data migration scenario completed successfully")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_disaster_recovery(self):
        """災害復旧テストのシミュレーション"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # フェーズ1: 正常運用時のデータ作成
                production_users = []
                for i in range(10):
                    user_data = UserCreate(
                        username=f"integration_prod_user_{i}",
                        email=f"prod.user{i}@integration.com",
                        password="prodpass123",
                        group=GroupEnum.CSC_1 if i < 5 else GroupEnum.CSC_2,
                        full_name=f"本番ユーザー{i}",
                        is_active=True,
                        is_admin=(i == 0),  # 最初のユーザーのみ管理者
                        is_sv=(i < 2)       # 最初の2ユーザーがSV
                    )
                    
                    prod_user = await user_crud.create_user(session, user_data)
                    
                    # 安全なデータ保存
                    user_info = {
                        'id': str(prod_user.id),
                        'username': prod_user.username,
                        'email': prod_user.email,
                        'full_name': prod_user.full_name,
                        'group': prod_user.group,
                        'is_active': prod_user.is_active,
                        'is_admin': prod_user.is_admin,
                        'is_sv': prod_user.is_sv
                    }
                    production_users.append(user_info)
                    await session.commit()
                
                # フェーズ2: データ整合性のスナップショット
                original_user_count = len(production_users)
                original_admin_count = sum(1 for u in production_users if u['is_admin'])
                original_sv_count = sum(1 for u in production_users if u['is_sv'])
                original_usernames = {u['username'] for u in production_users}
                original_emails = {u['email'] for u in production_users}
                
                # フェーズ3: 災害シミュレーション（一部データの削除）
                # 実際の災害復旧では外部バックアップから復元するが、
                # ここではデータ削除→再作成で復旧をシミュレート
                
                # 一部ユーザーの情報を保存（復旧用）
                backup_data = []
                for user in production_users[:5]:  # 最初の5ユーザーを「バックアップ」
                    backup_data.append({
                        "username": user['username'],
                        "email": user['email'],
                        "full_name": user['full_name'],
                        "group": user['group'],
                        "is_active": user['is_active'],
                        "is_admin": user['is_admin'],
                        "is_sv": user['is_sv']
                    })
                
                # 災害シミュレーション：一部データ削除
                await session.execute(text(
                    "DELETE FROM users WHERE username LIKE 'integration_prod_user_%' AND "
                    "username IN ('integration_prod_user_0', 'integration_prod_user_1', "
                    "'integration_prod_user_2', 'integration_prod_user_3', 'integration_prod_user_4')"
                ))
                await session.commit()
                
                # フェーズ4: 復旧確認
                remaining_users = await user_crud.get_all_users(session)
                remaining_prod_users = [u for u in remaining_users if u.username.startswith("integration_prod_user_")]
                assert len(remaining_prod_users) == 5  # 半分のデータが残存
                
                # フェーズ5: バックアップからの復旧
                recovered_users = []
                for backup_user_data in backup_data:
                    try:
                        recovery_data = UserCreate(
                            username=backup_user_data["username"],
                            email=backup_user_data["email"],
                            password="recovery123",  # 復旧時の新パスワード
                            group=backup_user_data["group"],
                            full_name=backup_user_data["full_name"],
                            is_active=backup_user_data["is_active"],
                            is_admin=backup_user_data["is_admin"],
                            is_sv=backup_user_data["is_sv"]
                        )
                        
                        recovered_user = await user_crud.create_user(session, recovery_data)
                        recovered_users.append(recovered_user)
                        await session.commit()
                        
                    except Exception as e:
                        await session.rollback()
                        print(f"Recovery failed for {backup_user_data['username']}: {e}")
                        continue
                
                # フェーズ6: 復旧後の整合性確認
                final_users = await user_crud.get_all_users(session)
                final_prod_users = [u for u in final_users if u.username.startswith("integration_prod_user_")]
                
                assert len(final_prod_users) == original_user_count  # 全ユーザー復旧
                
                final_admin_count = sum(1 for u in final_prod_users if u.is_admin)
                final_sv_count = sum(1 for u in final_prod_users if u.is_sv)
                final_usernames = {u.username for u in final_prod_users}
                final_emails = {u.email for u in final_prod_users}
                
                assert final_admin_count == original_admin_count
                assert final_sv_count == original_sv_count
                assert final_usernames == original_usernames
                assert final_emails == original_emails
                
                print("Disaster recovery scenario completed successfully")
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)