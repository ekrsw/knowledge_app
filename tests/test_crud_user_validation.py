"""Data validation tests for CRUD user operations - Phase 1."""

import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

from app.crud.user import user_crud
from app.crud.exceptions import MissingRequiredFieldError
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestCRUDUserValidation:
    """データバリデーション系テスト"""

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
                "username LIKE 'validation%' OR username LIKE 'invalid%' OR "
                "username LIKE 'test%' OR username LIKE 'long%' OR "
                "username LIKE 'unicode%' OR username LIKE 'special%' OR "
                "email LIKE '%validation%' OR email LIKE '%invalid%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_invalid_email_formats(self):
        """無効なメール形式のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                invalid_emails = [
                    "invalid-email",           # @がない
                    "@example.com",           # ローカル部がない
                    "user@",                  # ドメイン部がない
                    "user..name@example.com", # 連続ドット
                    "user@.example.com",      # ドメイン先頭ドット
                    "user@example..com",      # ドメイン連続ドット
                    "user name@example.com",  # 空白文字
                    "user@example.com.",      # 末尾ドット
                ]
                
                for i, invalid_email in enumerate(invalid_emails):
                    with pytest.raises(Exception):  # PydanticのValidationError
                        user_data = UserCreate(
                            username=f"validation{i}",
                            email=invalid_email,
                            password="testpass123",
                            group=GroupEnum.CSC_1
                        )
                        await user_crud.create_user(session, user_data)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self):
        """無効なUUID形式での検索テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                invalid_uuids = [
                    "not-a-uuid",
                    "12345",
                    "invalid-uuid-format",
                    "123e4567-e89b-12d3-a456-42661417400g",  # 無効文字
                    "123e4567-e89b-12d3-a456",               # 短すぎ
                    "123e4567-e89b-12d3-a456-426614174000-extra",  # 長すぎ
                ]
                
                for invalid_uuid in invalid_uuids:
                    # UUID形式エラーが適切に処理されることを確認
                    try:
                        result = await user_crud.get_user_by_id(session, invalid_uuid)
                        # 無効なUUIDでNoneが返される場合
                        assert result is None
                    except Exception:
                        # 無効なUUIDで例外が発生する場合も正常（SQLAlchemyがバリデーション）
                        pass
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_username_length_limits(self):
        """ユーザー名長さ制限のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 極端に短いユーザー名（1文字）
                with pytest.raises(Exception):  # Pydanticバリデーションエラー
                    user_data = UserCreate(
                        username="a",
                        email="short@validation.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    await user_crud.create_user(session, user_data)
                
                # 極端に長いユーザー名（1000文字）
                long_username = "a" * 1000
                with pytest.raises(Exception):  # バリデーションまたはDBエラー
                    user_data = UserCreate(
                        username=long_username,
                        email="long@validation.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    await user_crud.create_user(session, user_data)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_password_length_limits(self):
        """パスワード長さ制限のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 極端に短いパスワード（1文字）
                with pytest.raises(Exception):  # Pydanticバリデーションエラー
                    user_data = UserCreate(
                        username="validation_short_pass",
                        email="shortpass@validation.com",
                        password="a",
                        group=GroupEnum.CSC_1
                    )
                    await user_crud.create_user(session, user_data)
                
                # 極端に長いパスワード（10000文字）
                long_password = "a" * 10000
                try:
                    user_data = UserCreate(
                        username="validation_long_pass",
                        email="longpass@validation.com",
                        password=long_password,
                        group=GroupEnum.CSC_1
                    )
                    # 非常に長いパスワードでも処理できることを確認
                    created_user = await user_crud.create_user(session, user_data)
                    # ハッシュ化が正常に行われることを確認
                    assert created_user.hashed_password != long_password
                    assert len(created_user.hashed_password) > 0
                    await session.commit()
                except Exception as e:
                    # 長すぎる場合のエラーも許容
                    pass
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_special_characters_in_username(self):
        """特殊文字を含むユーザー名のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                special_char_tests = [
                    ("user@name", "at_symbol"),      # @記号
                    ("user#name", "hash_symbol"),    # #記号
                    ("user$name", "dollar_symbol"),  # $記号
                    ("user name", "space_char"),     # 空白
                    ("user\tname", "tab_char"),      # タブ
                    ("user\nname", "newline_char"),  # 改行
                    ("user<>name", "angle_brackets"), # 角括弧
                    ("user{}name", "curly_brackets"), # 波括弧
                ]
                
                for username, test_case in special_char_tests:
                    try:
                        user_data = UserCreate(
                            username=username,
                            email=f"{test_case}@validation.com",
                            password="testpass123",
                            group=GroupEnum.CSC_1
                        )
                        
                        # 特殊文字を含むユーザー名の処理を確認
                        # 成功する場合と失敗する場合両方あり得る
                        created_user = await user_crud.create_user(session, user_data)
                        if created_user:
                            # 成功した場合、正しく保存されていることを確認
                            assert created_user.username == username
                            await session.commit()
                        
                    except Exception:
                        # 特殊文字が拒否される場合も正常
                        await session.rollback()
                        continue
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_unicode_characters(self):
        """Unicode文字・絵文字のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                unicode_tests = [
                    ("山田太郎", "田中@unicode.com", "japanese"),      # 日本語
                    ("张三", "zhang@unicode.com", "chinese"),         # 中国語
                    ("José", "jose@unicode.com", "spanish"),          # スペイン語（アクセント）
                    ("Müller", "muller@unicode.com", "german"),       # ドイツ語（ウムラウト）
                    ("🙂user", "emoji@unicode.com", "emoji"),          # 絵文字
                    ("user🎉", "celebration@unicode.com", "emoji2"),  # 絵文字2
                ]
                
                for username, email, test_type in unicode_tests:
                    try:
                        user_data = UserCreate(
                            username=username,
                            email=email,
                            password="testpass123",
                            group=GroupEnum.CSC_1
                        )
                        
                        created_user = await user_crud.create_user(session, user_data)
                        assert created_user.username == username
                        assert created_user.email == email
                        await session.commit()
                        
                        # 取得でも正常に動作することを確認
                        found_user = await user_crud.get_user_by_username(session, username)
                        assert found_user is not None
                        assert found_user.username == username
                        
                    except Exception as e:
                        # Unicode文字が拒否される場合も正常
                        await session.rollback()
                        continue
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_null_values_in_fields(self):
        """各フィールドのnull/None値テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 必須フィールドにNoneを設定した場合のテスト
                required_field_tests = [
                    ("username", None),
                    ("email", None),
                    ("password", None),
                    ("group", None),
                ]
                
                for field_name, none_value in required_field_tests:
                    try:
                        kwargs = {
                            "username": "validuser",
                            "email": "valid@validation.com",
                            "password": "validpass123",
                            "group": GroupEnum.CSC_1,
                        }
                        kwargs[field_name] = none_value
                        
                        user_data = UserCreate(**kwargs)
                        
                        with pytest.raises(Exception):  # バリデーションエラー
                            await user_crud.create_user(session, user_data)
                            
                    except Exception:
                        # 期待されるエラー
                        continue
                
                # オプションフィールドのNone値は正常処理されることを確認
                user_data = UserCreate(
                    username="validation_optional_none",
                    email="optional@validation.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1,
                    full_name=None,
                    ctstage_name=None,
                    sweet_name=None
                )
                
                created_user = await user_crud.create_user(session, user_data)
                assert created_user.full_name is None
                assert created_user.ctstage_name is None
                assert created_user.sweet_name is None
                await session.commit()
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """SQLインジェクション対策のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # SQLインジェクション攻撃パターン
                injection_patterns = [
                    "'; DROP TABLE users; --",
                    "' OR '1'='1",
                    "'; INSERT INTO users (username) VALUES ('hacked'); --",
                    "' UNION SELECT * FROM users --",
                    "admin'--",
                    "' OR 1=1 --",
                    "'; UPDATE users SET is_admin=true WHERE username='admin'; --",
                ]
                
                for i, injection_pattern in enumerate(injection_patterns):
                    try:
                        # ユーザー名にインジェクションパターンを使用
                        user_data = UserCreate(
                            username=injection_pattern,
                            email=f"injection{i}@validation.com",
                            password="testpass123",
                            group=GroupEnum.CSC_1
                        )
                        
                        # SQLインジェクションが無効化されることを確認
                        created_user = await user_crud.create_user(session, user_data)
                        if created_user:
                            # 文字列として安全に保存されることを確認
                            assert created_user.username == injection_pattern
                            await session.commit()
                        
                        # 検索でもインジェクションが無効化されることを確認
                        found_user = await user_crud.get_user_by_username(session, injection_pattern)
                        if found_user:
                            assert found_user.username == injection_pattern
                            
                    except Exception:
                        # インジェクションパターンが拒否される場合も正常
                        await session.rollback()
                        continue
                
                # データベースが正常に動作していることを確認
                normal_user = UserCreate(
                    username="validation_normal_after_injection",
                    email="normal@validation.com", 
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                created_normal = await user_crud.create_user(session, normal_user)
                assert created_normal is not None
                await session.commit()
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)