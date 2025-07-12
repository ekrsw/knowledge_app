"""Security-related tests for CRUD user operations - Phase 1."""

import pytest
import pytest_asyncio
import time
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, pwd_context


class TestCRUDUserSecurity:
    """セキュリティ関連テスト"""

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
                "username LIKE 'security%' OR username LIKE 'hash%' OR "
                "username LIKE 'password%' OR username LIKE 'timing%' OR "
                "username LIKE 'auth%' OR email LIKE '%security%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_password_hashing_details(self):
        """パスワードハッシュ化の詳細検証"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                password = "testpassword123"
                user_data = UserCreate(
                    username="security_hash_test",
                    email="hash@security.com",
                    password=password,
                    group=GroupEnum.CSC_1
                )
                
                created_user = await user_crud.create_user(session, user_data)
                hashed_password = created_user.hashed_password
                await session.commit()
                
                # ハッシュ化されていることを確認
                assert hashed_password != password
                assert len(hashed_password) > 0
                
                # bcryptハッシュの形式確認 ($2b$rounds$salt+hash)
                bcrypt_pattern = r'^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$'
                assert re.match(bcrypt_pattern, hashed_password), f"Invalid bcrypt format: {hashed_password}"
                
                # ハッシュの強度確認（bcryptのコスト）
                cost_match = re.search(r'\$2[aby]\$(\d{2})\$', hashed_password)
                assert cost_match is not None
                cost = int(cost_match.group(1))
                assert cost >= 10, f"Bcrypt cost too low: {cost}"  # 最低限のセキュリティレベル
                
                # 検証関数でのパスワード確認
                assert verify_password(password, hashed_password)
                assert not verify_password("wrongpassword", hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_password_hash_uniqueness(self):
        """同じパスワードでも異なるハッシュが生成されることのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                password = "samepassword123"
                hashes = []
                
                # 同じパスワードで複数のユーザーを作成
                for i in range(3):
                    user_data = UserCreate(
                        username=f"security_unique_{i}",
                        email=f"unique{i}@security.com",
                        password=password,
                        group=GroupEnum.CSC_1
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    hashes.append(created_user.hashed_password)
                    await session.commit()
                
                # 全てのハッシュが異なることを確認（ソルトにより）
                assert len(set(hashes)) == 3, "Same password should generate different hashes"
                
                # 各ハッシュで元のパスワードが検証できることを確認
                for hash_value in hashes:
                    assert verify_password(password, hash_value)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_password_strength_requirements(self):
        """パスワード強度要件のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 弱いパスワードのテストケース
                weak_passwords = [
                    "123",          # 短すぎ
                    "abc",          # 短すぎ + 文字のみ
                    "password",     # 一般的すぎ
                    "12345678",     # 数字のみ
                    "abcdefgh",     # 文字のみ
                ]
                
                for i, weak_password in enumerate(weak_passwords):
                    try:
                        user_data = UserCreate(
                            username=f"security_weak_{i}",
                            email=f"weak{i}@security.com",
                            password=weak_password,
                            group=GroupEnum.CSC_1
                        )
                        
                        # 弱いパスワードでも作成される場合がある（現在の実装では制限なし）
                        created_user = await user_crud.create_user(session, user_data)
                        if created_user:
                            # 作成された場合でも、ハッシュ化は正常に行われていることを確認
                            assert created_user.hashed_password != weak_password
                            await session.commit()
                        
                    except Exception:
                        # 弱いパスワードが拒否される場合（Pydanticバリデーション）
                        await session.rollback()
                        continue
                
                # 強いパスワードは正常に処理されることを確認（16文字制限内）
                strong_passwords = [
                    "Strong@Pass123",    # 大小文字・数字・記号
                    "Secure!Pass24",     # 複雑
                    "C0mpl3x#Key",       # 特殊文字含む
                ]
                
                for i, strong_password in enumerate(strong_passwords):
                    user_data = UserCreate(
                        username=f"security_strong_{i}",
                        email=f"strong{i}@security.com",
                        password=strong_password,
                        group=GroupEnum.CSC_1
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    assert created_user is not None
                    assert created_user.hashed_password != strong_password
                    await session.commit()
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_sensitive_data_exposure(self):
        """機密情報漏洩防止のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                password = "sensitive123"  # 16文字制限内
                user_data = UserCreate(
                    username="security_exposure_test",
                    email="exposure@security.com",
                    password=password,
                    group=GroupEnum.CSC_1
                )
                
                created_user = await user_crud.create_user(session, user_data)
                await session.commit()
                
                # ユーザーオブジェクトに平文パスワードが含まれていないことを確認
                user_dict = created_user.__dict__
                for key, value in user_dict.items():
                    if isinstance(value, str):
                        assert password not in value, f"Plain password found in {key}: {value}"
                
                # ハッシュ化されたパスワードが保存されていることを確認
                assert created_user.hashed_password != password
                assert len(created_user.hashed_password) > 0
                
                # ログやエラーメッセージに平文パスワードが含まれないことを確認
                # (実際のログ出力は環境依存のため、基本的な確認のみ)
                try:
                    # 意図的にエラーを発生させてログ出力をテスト
                    duplicate_data = UserCreate(
                        username="security_exposure_test",  # 重複ユーザー名
                        email="duplicate@security.com",
                        password=password,
                        group=GroupEnum.CSC_2
                    )
                    await user_crud.create_user(session, duplicate_data)
                except Exception as e:
                    # エラーメッセージに平文パスワードが含まれていないことを確認
                    error_message = str(e)
                    assert password not in error_message, f"Password leaked in error: {error_message}"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_timing_attack_resistance(self):
        """タイミング攻撃対策のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 存在するユーザーを作成
                existing_user_data = UserCreate(
                    username="security_timing_existing",
                    email="existing@security.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                await user_crud.create_user(session, existing_user_data)
                await session.commit()
                
                # 存在するユーザーの検索時間を測定
                existing_times = []
                for _ in range(5):
                    start_time = time.time()
                    result = await user_crud.get_user_by_username(session, "security_timing_existing")
                    end_time = time.time()
                    existing_times.append(end_time - start_time)
                    assert result is not None
                
                # 存在しないユーザーの検索時間を測定
                nonexistent_times = []
                for i in range(5):
                    start_time = time.time()
                    result = await user_crud.get_user_by_username(session, f"nonexistent_user_{i}")
                    end_time = time.time()
                    nonexistent_times.append(end_time - start_time)
                    assert result is None
                
                # 平均処理時間を計算
                avg_existing = sum(existing_times) / len(existing_times)
                avg_nonexistent = sum(nonexistent_times) / len(nonexistent_times)
                
                # 時間差が過度に大きくないことを確認（タイミング攻撃対策）
                # 許容差は環境によって調整が必要
                time_ratio = max(avg_existing, avg_nonexistent) / min(avg_existing, avg_nonexistent)
                assert time_ratio < 10, f"Timing difference too large: {time_ratio}"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_authentication_integration(self):
        """認証との統合テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # ユーザー作成
                password = "authpass123"
                user_data = UserCreate(
                    username="security_auth_test",
                    email="auth@security.com",
                    password=password,
                    group=GroupEnum.CSC_1
                )
                
                created_user = await user_crud.create_user(session, user_data)
                await session.commit()
                
                # 認証シミュレーション
                # 1. ユーザー名でユーザーを取得
                found_user = await user_crud.get_user_by_username(session, "security_auth_test")
                assert found_user is not None
                
                # 2. パスワード検証
                assert verify_password(password, found_user.hashed_password)
                assert not verify_password("wrongpassword", found_user.hashed_password)
                
                # 3. ユーザーの状態確認
                assert found_user.is_active is True  # アクティブユーザーのみ認証可能
                
                # 非アクティブユーザーのテスト
                inactive_user_data = UserCreate(
                    username="security_auth_inactive",
                    email="inactive@security.com",
                    password=password,
                    group=GroupEnum.CSC_1,
                    is_active=False
                )
                
                inactive_user = await user_crud.create_user(session, inactive_user_data)
                await session.commit()
                
                # 非アクティブユーザーでも検索は可能
                found_inactive = await user_crud.get_user_by_username(session, "security_auth_inactive")
                assert found_inactive is not None
                assert found_inactive.is_active is False
                
                # パスワードは正しいが、is_activeをチェックして認証を制御
                assert verify_password(password, found_inactive.hashed_password)
                # アプリケーション側でis_activeをチェックする必要がある
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_password_hash_immutability(self):
        """パスワードハッシュの不変性テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                password = "immutable123"
                user_data = UserCreate(
                    username="security_immutable",
                    email="immutable@security.com",
                    password=password,
                    group=GroupEnum.CSC_1
                )
                
                created_user = await user_crud.create_user(session, user_data)
                original_hash = created_user.hashed_password
                original_id = created_user.id
                await session.commit()
                
                # 同じユーザーを再度取得
                retrieved_user = await user_crud.get_user_by_id(session, str(original_id))
                assert retrieved_user is not None
                
                # ハッシュが変更されていないことを確認
                assert retrieved_user.hashed_password == original_hash
                
                # 元のパスワードで検証可能であることを確認
                assert verify_password(password, retrieved_user.hashed_password)
                
                # 異なる類似パスワードでは検証失敗することを確認
                similar_passwords = [
                    "immutable124",    # 1文字違い
                    "Immutable123",    # 大文字違い
                    "immutable123 ",   # 末尾空白
                    " immutable123",   # 先頭空白
                ]
                
                for similar_password in similar_passwords:
                    assert not verify_password(similar_password, retrieved_user.hashed_password)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)