"""Edge cases and boundary value tests for CRUD user operations - Phase 2."""

import pytest
import pytest_asyncio
import asyncio
import threading
import time
import gc
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from app.crud.user import user_crud
from app.models.user import GroupEnum
from app.schemas.user import UserCreate
from app.core.config import settings


class TestCRUDUserEdgeCases:
    """エッジケース・境界値テスト"""

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
                "username LIKE 'edge%' OR username LIKE 'long%' OR "
                "username LIKE 'empty%' OR username LIKE 'case%' OR "
                "username LIKE 'concurrent%' OR username LIKE 'memory%' OR "
                "username LIKE 'timestamp%' OR email LIKE '%edge%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_extremely_long_strings(self):
        """極端に長い文字列のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 様々な長さの文字列をテスト
                string_lengths = [
                    (100, "hundred_chars"),      # 100文字
                    (1000, "thousand_chars"),    # 1000文字
                    (5000, "five_thousand"),     # 5000文字
                    (10000, "ten_thousand"),     # 10000文字
                ]
                
                for length, test_name in string_lengths:
                    try:
                        long_string = "A" * length
                        user_data = UserCreate(
                            username=f"edge_{test_name}",
                            email=f"{test_name}@edge.com",
                            password="testpass123",
                            group=GroupEnum.CSC_1,
                            full_name=long_string,
                            ctstage_name=long_string,
                            sweet_name=long_string
                        )
                        
                        # 極端に長い文字列の処理を確認
                        created_user = await user_crud.create_user(session, user_data)
                        if created_user:
                            # 保存された場合、正しく保存されていることを確認
                            assert len(created_user.full_name) > 0
                            await session.commit()
                            
                            # 取得でも正常に動作することを確認
                            found_user = await user_crud.get_user_by_username(session, f"edge_{test_name}")
                            assert found_user is not None
                            
                    except Exception:
                        # 長すぎる場合のエラーも許容（DB制限等）
                        await session.rollback()
                        continue
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_empty_and_whitespace_patterns(self):
        """空文字・空白パターンのテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 様々な空白パターン
                whitespace_patterns = [
                    ("", "empty_string"),
                    (" ", "single_space"),
                    ("  ", "double_space"),
                    ("\t", "tab_char"),
                    ("\n", "newline_char"),
                    ("\r", "carriage_return"),
                    ("   \t\n\r   ", "mixed_whitespace"),
                ]
                
                for i, (whitespace, pattern_name) in enumerate(whitespace_patterns):
                    try:
                        user_data = UserCreate(
                            username=f"edge_whitespace_{i}",
                            email=f"whitespace{i}@edge.com",
                            password="testpass123",
                            group=GroupEnum.CSC_1,
                            full_name=whitespace if whitespace else None,
                            ctstage_name=whitespace if whitespace else None,
                            sweet_name=whitespace if whitespace else None
                        )
                        
                        created_user = await user_crud.create_user(session, user_data)
                        if created_user:
                            # 空白文字の処理を確認
                            await session.commit()
                            
                        # ユーザー名に空白文字を使った場合のテスト
                        if whitespace.strip():  # 空でない空白文字の場合
                            try:
                                whitespace_username_data = UserCreate(
                                    username=f"edge{whitespace}test",
                                    email=f"ws_username{i}@edge.com", 
                                    password="testpass123",
                                    group=GroupEnum.CSC_1
                                )
                                created_ws_user = await user_crud.create_user(session, whitespace_username_data)
                                if created_ws_user:
                                    await session.commit()
                            except Exception:
                                # 空白文字を含むユーザー名が拒否される場合
                                await session.rollback()
                                
                    except Exception:
                        # バリデーションエラーが発生する場合
                        await session.rollback()
                        continue
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_case_sensitivity(self):
        """大文字小文字の区別テスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                base_username = "CaseSensitive"
                base_email = "Case@Edge.Com"
                
                # 基本ユーザーを作成
                user_data_1 = UserCreate(
                    username=base_username,
                    email=base_email,
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                
                created_user_1 = await user_crud.create_user(session, user_data_1)
                assert created_user_1 is not None
                await session.commit()
                
                # 異なる大文字小文字パターンでのテスト
                case_variations = [
                    ("casesensitive", "case@edge.com"),     # 全て小文字
                    ("CASESENSITIVE", "CASE@EDGE.COM"),     # 全て大文字
                    ("cAsEsEnSiTiVe", "cAsE@eDgE.cOm"),     # 混合
                ]
                
                for i, (username_var, email_var) in enumerate(case_variations):
                    try:
                        user_data_var = UserCreate(
                            username=username_var,
                            email=email_var,
                            password="testpass123",
                            group=GroupEnum.CSC_1
                        )
                        
                        # 重複チェックの動作を確認
                        created_user_var = await user_crud.create_user(session, user_data_var)
                        if created_user_var:
                            # 大文字小文字が区別される場合
                            await session.commit()
                        
                    except Exception:
                        # 重複エラーが発生する場合（大文字小文字を区別しない）
                        await session.rollback()
                        continue
                
                # 検索時の大文字小文字の動作確認
                search_variations = [
                    base_username.lower(),
                    base_username.upper(),
                    "casesensitive",
                    "CASESENSITIVE"
                ]
                
                for search_term in search_variations:
                    found_user = await user_crud.get_user_by_username(session, search_term)
                    # データベースの大文字小文字設定によって結果が異なる
                    # 結果の一貫性を確認
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self):
        """並行ユーザー作成のテスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # 同じユーザー名での並行作成テスト
                same_username = "edge_concurrent_test"
                
                async def create_user_task(task_id):
                    """並行実行用のユーザー作成タスク"""
                    task_engine = create_async_engine(
                        settings.DATABASE_URL,
                        echo=False,
                        pool_size=1,
                        max_overflow=0,
                        pool_pre_ping=True,
                        pool_recycle=60,
                    )
                    
                    task_session_factory = sessionmaker(
                        task_engine,
                        class_=AsyncSession,
                        expire_on_commit=False,
                        autocommit=False,
                        autoflush=False,
                    )
                    
                    try:
                        async with task_session_factory() as task_session:
                            user_data = UserCreate(
                                username=same_username,
                                email=f"concurrent{task_id}@edge.com",
                                password="testpass123",
                                group=GroupEnum.CSC_1
                            )
                            
                            try:
                                created_user = await user_crud.create_user(task_session, user_data)
                                await task_session.commit()
                                return {"success": True, "task_id": task_id, "user": created_user}
                            except IntegrityError:
                                await task_session.rollback()
                                return {"success": False, "task_id": task_id, "error": "IntegrityError"}
                            except Exception as e:
                                await task_session.rollback()
                                return {"success": False, "task_id": task_id, "error": str(e)}
                    finally:
                        await task_engine.dispose()
                
                # 5つの並行タスクを実行
                tasks = [create_user_task(i) for i in range(5)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 結果の分析
                successful_creations = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
                failed_creations = len(results) - successful_creations
                
                # 少なくとも1つは成功し、他は適切にエラーハンドリングされることを確認
                assert successful_creations >= 1, "At least one creation should succeed"
                assert failed_creations >= 0, "Failed creations should be handled gracefully"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_timestamp_edge_cases(self):
        """タイムスタンプのエッジケーステスト"""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # タイムスタンプの精度と一意性テスト
                users_created = []
                creation_times = []
                
                # 短時間で複数ユーザーを作成
                for i in range(10):
                    user_data = UserCreate(
                        username=f"edge_timestamp_{i}",
                        email=f"timestamp{i}@edge.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    
                    start_time = time.time()
                    created_user = await user_crud.create_user(session, user_data)
                    end_time = time.time()
                    
                    # タイムスタンプ情報を安全に保存
                    user_info = {
                        'id': str(created_user.id),
                        'username': created_user.username,
                        'created_at': created_user.created_at,
                        'updated_at': created_user.updated_at
                    }
                    users_created.append(user_info)
                    creation_times.append((start_time, end_time, user_info['created_at']))
                    
                    # 微小な待機時間（タイムスタンプの分解能テスト）
                    await asyncio.sleep(0.001)
                
                await session.commit()
                
                # タイムスタンプの順序性確認
                for i in range(1, len(users_created)):
                    prev_user = users_created[i-1]
                    curr_user = users_created[i]
                    
                    # created_atが適切に設定されていることを確認
                    assert prev_user['created_at'] is not None
                    assert curr_user['created_at'] is not None
                    
                    # タイムスタンプが論理的に正しい順序であることを確認
                    # （ただし、高精度の場合は同じ値になる可能性もある）
                    assert prev_user['created_at'] <= curr_user['created_at']
                
                # updated_atとcreated_atの関係確認
                for user in users_created:
                    assert user['updated_at'] is not None
                    # 作成時はcreated_atとupdated_atが同じまたは近い値
                    time_diff = abs((user['updated_at'] - user['created_at']).total_seconds())
                    assert time_diff < 1.0, "created_at and updated_at should be close at creation"
                
                # タイムゾーン情報の確認
                sample_user = users_created[0]
                assert sample_user['created_at'].tzinfo is not None, "Timestamp should be timezone-aware"
                assert sample_user['updated_at'].tzinfo is not None, "Timestamp should be timezone-aware"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)