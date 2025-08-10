"""
パフォーマンステスト - 基本版

基本的なパフォーマンス要件を検証する軽量版テスト
"""

import asyncio
import time
from typing import List, Dict, Any
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.auth import create_test_user_and_token


@pytest.mark.performance
class TestBasicPerformance:
    """基本パフォーマンステスト"""
    
    @pytest.mark.asyncio
    async def test_api_response_time_basic(self, client: AsyncClient, db_session: AsyncSession):
        """基本的なAPI応答時間テスト（1秒以内要件）"""
        # テスト用ユーザー作成
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        # API応答時間測定
        start_time = time.time()
        
        response = await client.get(
            "/api/v1/revisions/",
            params={"skip": 0, "limit": 10},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # アサーション
        assert response.status_code == 200
        assert response_time < 1.0, f"基本API応答時間が長すぎます: {response_time:.3f}秒（要件: 1秒以内）"
        
        print(f"PASS - 基本API応答時間テスト完了 - 応答時間: {response_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_multiple_api_calls_performance(self, client: AsyncClient, db_session: AsyncSession):
        """複数API呼び出しパフォーマンステスト"""
        # テスト用ユーザー作成
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        # 10回のAPI呼び出し実行
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            
            response = await client.get(
                "/api/v1/articles/",
                params={"skip": i * 5, "limit": 5},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            assert response.status_code == 200
        
        # 統計計算
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # アサーション
        assert avg_response_time < 0.5, f"平均応答時間が長すぎます: {avg_response_time:.3f}秒"
        assert max_response_time < 1.0, f"最大応答時間が長すぎます: {max_response_time:.3f}秒"
        
        print(f"PASS - 複数API呼び出しテスト完了 - 平均: {avg_response_time:.3f}秒, 最大: {max_response_time:.3f}秒, 最小: {min_response_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_basic(self, client: AsyncClient, db_session: AsyncSession):
        """基本的な並行リクエストテスト"""
        # テスト用ユーザー作成
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        async def single_request(request_id: int) -> Dict[str, Any]:
            """単一リクエスト"""
            start_time = time.time()
            
            try:
                response = await client.get(
                    "/api/v1/system/health",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                end_time = time.time()
                
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "status_code": 500,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # 5並行リクエスト実行
        start_time = time.time()
        
        tasks = [single_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # 結果分析
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        
        # アサーション
        success_rate = len(successful_requests) / len(results)
        assert success_rate >= 0.8, f"成功率が低すぎます: {success_rate:.2%}（要件: 80%以上）"
        assert avg_response_time < 2.0, f"平均応答時間が長すぎます: {avg_response_time:.3f}秒"
        
        print(f"PASS - 並行リクエストテスト完了 - 成功率: {success_rate:.2%}, 平均応答時間: {avg_response_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_pagination_basic_performance(self, client: AsyncClient, db_session: AsyncSession):
        """基本ページネーション性能テスト"""
        # テスト用ユーザー作成
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        # 異なるページサイズでテスト
        page_sizes = [10, 25, 50]
        results = {}
        
        for page_size in page_sizes:
            response_times = []
            
            # 各ページサイズで3ページテスト
            for page_num in range(3):
                skip = page_num * page_size
                
                start_time = time.time()
                
                response = await client.get(
                    "/api/v1/users/",
                    params={"skip": skip, "limit": page_size},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                assert response.status_code == 200
            
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            results[page_size] = {
                "avg_time": avg_time,
                "max_time": max_time
            }
            
            # パフォーマンス要件チェック
            assert avg_time < 1.0, f"ページサイズ{page_size}の平均応答時間が長すぎます: {avg_time:.3f}秒"
        
        # 結果表示
        print("✓ ページネーション性能テスト完了:")
        for page_size, result in results.items():
            print(f"  - ページサイズ{page_size}: 平均{result['avg_time']:.3f}秒, 最大{result['max_time']:.3f}秒")
    
    @pytest.mark.asyncio 
    async def test_authentication_performance(self, client: AsyncClient, db_session: AsyncSession):
        """認証パフォーマンステスト"""
        # テスト用ユーザー作成
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        # 認証が必要なAPIを10回呼び出し
        auth_response_times = []
        
        for i in range(10):
            start_time = time.time()
            
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            auth_response_times.append(response_time)
            
            assert response.status_code == 200
        
        # 統計
        avg_auth_time = sum(auth_response_times) / len(auth_response_times)
        max_auth_time = max(auth_response_times)
        
        # アサーション
        assert avg_auth_time < 0.3, f"認証処理の平均時間が長すぎます: {avg_auth_time:.3f}秒"
        assert max_auth_time < 0.5, f"認証処理の最大時間が長すぎます: {max_auth_time:.3f}秒"
        
        print(f"PASS - 認証パフォーマンステスト完了 - 平均: {avg_auth_time:.3f}秒, 最大: {max_auth_time:.3f}秒")


@pytest.mark.performance
class TestMemoryPerformance:
    """メモリ性能テスト"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_basic(self, client: AsyncClient, db_session: AsyncSession):
        """Basic memory usage test"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create test user
            admin_user, token = await create_test_user_and_token(db_session, role="admin")
            
            # Execute multiple API requests (check for memory leaks)
            for i in range(20):
                response = await client.get(
                    "/api/v1/system/health",
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 200
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Ensure memory usage doesn't increase excessively
            assert memory_increase < 50, f"Memory usage increased excessively: {memory_increase:.2f}MB"
            
            print(f"PASS - Memory usage test completed - initial: {initial_memory:.1f}MB, final: {final_memory:.1f}MB, increase: {memory_increase:.1f}MB")
            
        except ImportError:
            pytest.skip("psutil not available - memory test skipped")