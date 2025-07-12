"""Optional fields tests for CRUD user operations - Phase 1."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from itertools import product

from app.crud.user import user_crud
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestCRUDUserOptionalFields:
    """オプションフィールド詳細テスト"""

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
                "username LIKE 'optional%' OR username LIKE 'combo%' OR "
                "username LIKE 'permission%' OR username LIKE 'default%' OR "
                "username LIKE 'field%' OR email LIKE '%optional%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_optional_fields_combinations(self):
        """オプションフィールドの全組み合わせテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # オプションフィールドの値パターン
                full_name_options = [None, "田中太郎"]
                ctstage_name_options = [None, "開発ステージ"]
                sweet_name_options = [None, "スイート名"]
                
                # 全組み合わせをテスト（2^3 = 8通り）
                combinations = list(product(full_name_options, ctstage_name_options, sweet_name_options))
                
                for i, (full_name, ctstage_name, sweet_name) in enumerate(combinations):
                    user_data = UserCreate(
                        username=f"optional_combo_{i}",
                        email=f"combo{i}@optional.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1,
                        full_name=full_name,
                        ctstage_name=ctstage_name,
                        sweet_name=sweet_name
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # 値が正しく設定されていることを確認
                    assert created_user.full_name == full_name
                    assert created_user.ctstage_name == ctstage_name
                    assert created_user.sweet_name == sweet_name
                    
                    await session.commit()
                    
                    # 取得でも正しい値が得られることを確認
                    found_user = await user_crud.get_user_by_username(session, f"optional_combo_{i}")
                    assert found_user is not None
                    assert found_user.full_name == full_name
                    assert found_user.ctstage_name == ctstage_name
                    assert found_user.sweet_name == sweet_name
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_permission_flags_combinations(self):
        """権限フラグの全組み合わせテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 権限フラグの全組み合わせ（2^3 = 8通り）
                boolean_options = [True, False]
                combinations = list(product(boolean_options, boolean_options, boolean_options))
                
                for i, (is_active, is_admin, is_sv) in enumerate(combinations):
                    user_data = UserCreate(
                        username=f"permission_combo_{i}",
                        email=f"permission{i}@optional.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1,
                        is_active=is_active,
                        is_admin=is_admin,
                        is_sv=is_sv
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # 権限フラグが正しく設定されていることを確認
                    assert created_user.is_active == is_active
                    assert created_user.is_admin == is_admin
                    assert created_user.is_sv == is_sv
                    
                    await session.commit()
                    
                    # 取得でも正しい値が得られることを確認
                    found_user = await user_crud.get_user_by_username(session, f"permission_combo_{i}")
                    assert found_user is not None
                    assert found_user.is_active == is_active
                    assert found_user.is_admin == is_admin
                    assert found_user.is_sv == is_sv
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_optional_fields_null_to_value(self):
        """Null→値の更新パターンテスト（将来の更新機能用）"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 初期状態：オプションフィールドがNullのユーザーを作成
                user_data = UserCreate(
                    username="optional_null_to_value",
                    email="nulltovalue@optional.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1,
                    full_name=None,
                    ctstage_name=None,
                    sweet_name=None
                )
                
                created_user = await user_crud.create_user(session, user_data)
                user_id = created_user.id
                
                # 初期状態の確認
                assert created_user.full_name is None
                assert created_user.ctstage_name is None
                assert created_user.sweet_name is None
                
                await session.commit()
                
                # データベースから再取得して確認
                retrieved_user = await user_crud.get_user_by_id(session, str(user_id))
                assert retrieved_user is not None
                assert retrieved_user.full_name is None
                assert retrieved_user.ctstage_name is None
                assert retrieved_user.sweet_name is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_optional_fields_validation(self):
        """オプションフィールドのバリデーションテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 有効な値でのテスト
                valid_values = [
                    ("山田太郎", "本番環境", "メインスイート"),      # 日本語
                    ("John Doe", "Production", "Main Suite"),     # 英語
                    ("José García", "Producción", "Suite Principal"),  # アクセント付き
                    ("", "", ""),  # 空文字列
                ]
                
                for i, (full_name, ctstage_name, sweet_name) in enumerate(valid_values):
                    user_data = UserCreate(
                        username=f"optional_valid_{i}",
                        email=f"valid{i}@optional.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1,
                        full_name=full_name if full_name else None,
                        ctstage_name=ctstage_name if ctstage_name else None,
                        sweet_name=sweet_name if sweet_name else None
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    assert created_user is not None
                    await session.commit()
                
                # 極端に長い値でのテスト
                long_text = "A" * 1000  # 1000文字
                try:
                    user_data = UserCreate(
                        username="optional_long_text",
                        email="longtext@optional.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1,
                        full_name=long_text,
                        ctstage_name=long_text,
                        sweet_name=long_text
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    # 長いテキストが正常に処理される、または適切にエラーになる
                    if created_user:
                        assert created_user.full_name == long_text
                        await session.commit()
                        
                except Exception:
                    # 長すぎる場合のエラーも許容
                    await session.rollback()
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_admin_permission_logic(self):
        """管理者権限のロジックテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 一般的な権限パターンのテスト
                permission_scenarios = [
                    # (is_active, is_admin, is_sv, scenario_name)
                    (True, False, False, "normal_active_user"),      # 一般アクティブユーザー
                    (False, False, False, "inactive_user"),          # 非アクティブユーザー
                    (True, True, False, "admin_user"),               # 管理者
                    (True, True, True, "admin_sv_user"),             # 管理者兼SV
                    (True, False, True, "sv_user"),                  # SVのみ
                    (False, True, False, "inactive_admin"),          # 非アクティブ管理者
                    (False, False, True, "inactive_sv"),             # 非アクティブSV
                    (False, True, True, "inactive_admin_sv"),        # 非アクティブ管理者兼SV
                ]
                
                for i, (is_active, is_admin, is_sv, scenario) in enumerate(permission_scenarios):
                    user_data = UserCreate(
                        username=f"optional_perm_{scenario}",
                        email=f"perm{i}@optional.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1,
                        is_active=is_active,
                        is_admin=is_admin,
                        is_sv=is_sv
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # 権限の組み合わせが正しく保存されることを確認
                    assert created_user.is_active == is_active
                    assert created_user.is_admin == is_admin
                    assert created_user.is_sv == is_sv
                    
                    await session.commit()
                    
                    # 業務ロジックの確認（例：管理者は通常アクティブであるべき）
                    if is_admin and not is_active:
                        # 非アクティブな管理者が作成された場合の注意点
                        # 実際の業務では、このような組み合わせを制限するかもしれない
                        pass  # 現在は制限なしで許可
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_default_values_behavior(self):
        """デフォルト値の動作テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 最小限の必須フィールドのみでユーザー作成
                user_data = UserCreate(
                    username="optional_defaults",
                    email="defaults@optional.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                    # オプションフィールドは指定しない
                )
                
                created_user = await user_crud.create_user(session, user_data)
                
                # Pydanticのデフォルト値が適用されていることを確認
                assert created_user.full_name is None
                assert created_user.ctstage_name is None
                assert created_user.sweet_name is None
                assert created_user.is_active is True    # デフォルト値
                assert created_user.is_admin is False    # デフォルト値
                assert created_user.is_sv is False       # デフォルト値
                
                # データベース生成フィールドが設定されていることを確認
                assert created_user.id is not None
                assert created_user.created_at is not None
                assert created_user.updated_at is not None
                assert created_user.hashed_password is not None
                assert created_user.hashed_password != "testpass123"
                
                await session.commit()
                
                # データベースから再取得してデフォルト値を確認
                found_user = await user_crud.get_user_by_username(session, "optional_defaults")
                assert found_user is not None
                assert found_user.is_active is True
                assert found_user.is_admin is False
                assert found_user.is_sv is False
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_group_enum_values(self):
        """GroupEnumの各値でのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 全GroupEnum値でのユーザー作成
                group_values = [GroupEnum.CSC_1, GroupEnum.CSC_2, GroupEnum.CSC_N, GroupEnum.HHD]
                
                for i, group in enumerate(group_values):
                    user_data = UserCreate(
                        username=f"optional_group_{group.name}",
                        email=f"group{i}@optional.com",
                        password="testpass123",
                        group=group,
                        full_name=f"グループ{group.name}ユーザー",
                        ctstage_name=f"{group.name}ステージ",
                        sweet_name=f"{group.name}スイート"
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # グループが正しく設定されていることを確認
                    assert created_user.group == group
                    assert created_user.group.name == group.name
                    
                    await session.commit()
                    
                    # 取得でも正しいグループが得られることを確認
                    found_user = await user_crud.get_user_by_username(session, f"optional_group_{group.name}")
                    assert found_user is not None
                    assert found_user.group == group
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_complex_field_combinations(self):
        """複雑なフィールド組み合わせテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 実用的な組み合わせパターン
                realistic_scenarios = [
                    {
                        "username": "optional_scenario_admin",
                        "email": "admin@optional.com",
                        "full_name": "システム管理者",
                        "ctstage_name": "本番環境",
                        "sweet_name": "管理スイート",
                        "group": GroupEnum.HHD,
                        "is_active": True,
                        "is_admin": True,
                        "is_sv": False
                    },
                    {
                        "username": "optional_scenario_developer",
                        "email": "dev@optional.com",
                        "full_name": "開発者田中",
                        "ctstage_name": "開発環境",
                        "sweet_name": "開発スイート",
                        "group": GroupEnum.CSC_1,
                        "is_active": True,
                        "is_admin": False,
                        "is_sv": True
                    },
                    {
                        "username": "optional_scenario_temp",
                        "email": "temp@optional.com",
                        "full_name": None,  # 一時ユーザー
                        "ctstage_name": None,
                        "sweet_name": None,
                        "group": GroupEnum.CSC_N,
                        "is_active": False,
                        "is_admin": False,
                        "is_sv": False
                    }
                ]
                
                for scenario in realistic_scenarios:
                    scenario["password"] = "testpass123"
                    user_data = UserCreate(**scenario)
                    
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # 全フィールドが正しく設定されていることを確認
                    for field, expected_value in scenario.items():
                        if field != "password":  # パスワードはハッシュ化される
                            actual_value = getattr(created_user, field)
                            assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"
                    
                    await session.commit()
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)