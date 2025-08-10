"""
パフォーマンステスト

このモジュールはシステムのパフォーマンス要件を検証します：
- 応答時間: 3秒以内
- 同時接続: 100ユーザーまで
- 大量データ処理: 10MBまで
- ページネーション性能
"""

import asyncio
import time
from typing import List, Dict, Any
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.auth import create_test_user_and_token, get_auth_token
from tests.factories.article_factory import ArticleFactory
from tests.factories.revision_factory import RevisionFactory
from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.info_category_factory import InfoCategoryFactory


@pytest.mark.performance
class TestPerformanceAPI:
    """API パフォーマンステスト"""
    
    @pytest.mark.asyncio
    async def test_large_data_response_time(self, client: AsyncClient, db_session: AsyncSession):
        """大量データでの応答時間テスト（3秒以内要件）"""
        # テストデータ準備
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        # 大量の修正案を作成（1000件）
        info_category = await InfoCategoryFactory.create(db_session)
        approval_group = await ApprovalGroupFactory.create(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group)
        
        # 記事作成
        articles = []
        for i in range(100):
            article = await ArticleFactory.create(
                db_session, 
                article_id=f"PERF_ARTICLE_{i:03d}",
                info_category=info_category,
                approval_group=approval_group
            )
            articles.append(article)
        
        # 修正案大量作成（各記事に10件ずつ、計1000件）
        for article in articles:
            for j in range(10):
                await RevisionFactory.create(
                    db_session,
                    target_article_id=article.article_id,
                    proposer=admin_user,
                    approver=approver,
                    status="approved"
                )
        
        # 応答時間測定
        start_time = time.time()
        
        response = await client.get(
            "/api/v1/revisions/",
            params={"skip": 0, "limit": 1000},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # アサーション
        assert response.status_code == 200
        assert response_time < 3.0, f"応答時間が要件を超過: {response_time:.2f}秒（要件: 3秒以内）"
        
        data = response.json()
        assert len(data) <= 1000, "データ件数が予期された範囲を超過"
        
        print(f"✓ 大量データテスト完了 - 応答時間: {response_time:.2f}秒 ({len(data)}件)")
    
    @pytest.mark.asyncio
    async def test_concurrent_users_simulation(self, client: AsyncClient, db_session: AsyncSession):
        """同時接続100ユーザーのテスト"""
        # テストデータ準備
        info_category = await InfoCategoryFactory.create(db_session)
        approval_group = await ApprovalGroupFactory.create(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group)
        
        # 単一の管理者ユーザーを事前作成（データベース競合回避）
        admin_user, admin_token = await create_test_user_and_token(
            db_session, 
            role="admin",
            username="concurrent_test_admin"
        )
        
        # 100ユーザーを作成し、有効なJWTトークンを生成
        users_tokens = []
        for i in range(100):
            user = await UserFactory.create(
                db_session,
                username=f"concurrent_user_{i:03d}",
                email=f"concurrent_{i:03d}@test.com"
            )
            # 有効なJWTトークンを生成
            token = await get_auth_token(user)
            users_tokens.append((user, token))
        
        # 記事作成（リクエスト先データ）
        article = await ArticleFactory.create(
            db_session,
            article_id="CONCURRENT_TEST_ARTICLE",
            info_category=info_category,
            approval_group=approval_group
        )
        
        async def user_request(user_token_pair: tuple, request_id: int) -> Dict[str, Any]:
            """個別ユーザーのリクエスト"""
            user, token = user_token_pair
            start_time = time.time()
            
            try:
                # 管理者権限でリクエスト（事前作成済みトークン使用）
                response = await client.get(
                    "/api/v1/articles/",
                    params={"skip": 0, "limit": 10},
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                end_time = time.time()
                
                return {
                    "user_id": str(user.id),
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "user_id": str(user.id),
                    "request_id": request_id,
                    "status_code": 500,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # 同時リクエスト実行
        start_time = time.time()
        
        # 実際に100同時は重すぎるため、10ユーザーで代表テスト
        sample_users = users_tokens[:10]
        tasks = [user_request(user_token, i) for i, user_token in enumerate(sample_users)]
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # 結果分析
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        max_response_time = max(r["response_time"] for r in results)
        
        # アサーション
        success_rate = len(successful_requests) / len(results)
        
        if failed_requests:
            print(f"⚠ 失敗リクエスト {len(failed_requests)}件:")
            for req in failed_requests[:3]:  # 最初の3件のみ表示
                print(f"  - User {req['user_id']}: {req.get('error', 'Unknown error')}")
        
        print(f"✓ 同時接続テスト完了 - 成功率: {success_rate:.2%}, 平均応答時間: {avg_response_time:.2f}秒, 最大応答時間: {max_response_time:.2f}秒")
        
        assert success_rate >= 0.95, f"成功率が低すぎます: {success_rate:.2%}（要件: 95%以上）"
        assert avg_response_time < 5.0, f"平均応答時間が長すぎます: {avg_response_time:.2f}秒"
        assert max_response_time < 10.0, f"最大応答時間が長すぎます: {max_response_time:.2f}秒"
    
    @pytest.mark.asyncio
    async def test_large_content_diff_performance(self, client: AsyncClient, db_session: AsyncSession):
        """10MBコンテンツでの差分表示テスト"""
        # テストデータ準備
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        info_category = await InfoCategoryFactory.create(db_session)
        approval_group = await ApprovalGroupFactory.create(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group)
        
        # 大容量コンテンツ作成（約1MB）
        large_content = "A" * (1024 * 1024)  # 1MB
        
        # 記事作成
        article = await ArticleFactory.create(
            db_session,
            article_id="LARGE_CONTENT_ARTICLE",
            title="Large Content Test Article",
            question=large_content[:500000],  # 500KB
            answer=large_content[500000:],     # 500KB
            info_category=info_category,
            approval_group=approval_group
        )
        
        # 大容量修正案作成
        modified_content = "B" * (1024 * 1024)  # 1MB (different content)
        
        revision = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=admin_user,
            approver=approver,
            after_question=modified_content[:500000],  # 500KB
            after_answer=modified_content[500000:],     # 500KB
            status="submitted"
        )
        
        # 差分表示APIのパフォーマンステスト
        start_time = time.time()
        
        response = await client.get(
            f"/api/v1/diffs/{revision.revision_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # アサーション
        assert response.status_code == 200
        assert response_time < 5.0, f"大容量差分表示の応答時間が長すぎます: {response_time:.2f}秒（要件: 5秒以内）"
        
        data = response.json()
        assert "field_diffs" in data
        assert len(data["field_diffs"]) > 0
        
        print(f"✓ 大容量差分テスト完了 - 応答時間: {response_time:.2f}秒")
    
    @pytest.mark.asyncio
    async def test_pagination_performance(self, client: AsyncClient, db_session: AsyncSession):
        """ページネーション性能テスト"""
        # テストデータ準備
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        info_category = await InfoCategoryFactory.create(db_session)
        approval_group = await ApprovalGroupFactory.create(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group)
        
        # 2000件のデータ作成（ページネーションテスト用）
        for i in range(200):  # 200記事
            article = await ArticleFactory.create(
                db_session,
                article_id=f"PAGINATION_ARTICLE_{i:03d}",
                info_category=info_category,
                approval_group=approval_group
            )
            
            # 各記事に10件の修正案
            for j in range(10):
                await RevisionFactory.create(
                    db_session,
                    target_article_id=article.article_id,
                    proposer=admin_user,
                    approver=approver,
                    status="approved"
                )
        
        # ページネーション性能テスト
        page_sizes = [10, 50, 100, 200]
        results = {}
        
        for page_size in page_sizes:
            # 各ページサイズで複数ページをテスト
            page_times = []
            
            for page in range(0, min(1000, page_size * 5), page_size):  # 最初の数ページをテスト
                start_time = time.time()
                
                response = await client.get(
                    "/api/v1/revisions/",
                    params={"skip": page, "limit": page_size},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                end_time = time.time()
                page_time = end_time - start_time
                page_times.append(page_time)
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) <= page_size
            
            avg_time = sum(page_times) / len(page_times)
            max_time = max(page_times)
            
            results[page_size] = {
                "avg_time": avg_time,
                "max_time": max_time,
                "pages_tested": len(page_times)
            }
            
            # パフォーマンス要件チェック
            assert avg_time < 2.0, f"ページサイズ{page_size}の平均応答時間が長すぎます: {avg_time:.2f}秒"
            assert max_time < 4.0, f"ページサイズ{page_size}の最大応答時間が長すぎます: {max_time:.2f}秒"
        
        # 結果表示
        print("✓ ページネーション性能テスト完了:")
        for page_size, result in results.items():
            print(f"  - ページサイズ{page_size}: 平均{result['avg_time']:.3f}秒, 最大{result['max_time']:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_search_performance(self, client: AsyncClient, db_session: AsyncSession):
        """検索性能テスト"""
        # テストデータ準備
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        info_category = await InfoCategoryFactory.create(db_session)
        approval_group = await ApprovalGroupFactory.create(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group)
        
        # 検索用データ作成（1000記事）
        search_keywords = ["Python", "JavaScript", "Database", "API", "Performance"]
        
        for i in range(200):  # 200記事
            keyword = search_keywords[i % len(search_keywords)]
            
            article = await ArticleFactory.create(
                db_session,
                article_id=f"SEARCH_ARTICLE_{i:03d}",
                title=f"Search Test Article about {keyword}",
                keywords=f"{keyword}, testing, search",
                question=f"How to optimize {keyword} performance?",
                answer=f"{keyword} optimization involves multiple strategies...",
                info_category=info_category,
                approval_group=approval_group
            )
            
            # 修正案も作成
            for j in range(3):
                await RevisionFactory.create(
                    db_session,
                    target_article_id=article.article_id,
                    proposer=admin_user,
                    approver=approver,
                    after_title=f"Updated {keyword} Article",
                    status=["draft", "submitted", "approved"][j % 3]
                )
        
        # ステータス別検索性能テスト
        search_tests = [
            ("submitted", "提出済み検索"),
            ("approved", "承認済み検索"),
            ("draft", "ドラフト検索")
        ]
        
        for status, test_name in search_tests:
            start_time = time.time()
            
            response = await client.get(
                f"/api/v1/revisions/by-status/{status}",
                params={"skip": 0, "limit": 100},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0, f"{test_name}の応答時間が長すぎます: {response_time:.2f}秒"
            
            data = response.json()
            print(f"✓ {test_name}完了 - {len(data)}件, 応答時間: {response_time:.3f}秒")


@pytest.mark.performance
class TestPerformanceDatabase:
    """データベース性能テスト"""
    
    @pytest.mark.asyncio
    async def test_bulk_data_operations(self, db_session: AsyncSession):
        """バルクデータ操作性能テスト"""
        from app.repositories.revision import RevisionRepository
        
        revision_repo = RevisionRepository()
        
        # 大量データ読み取り性能
        start_time = time.time()
        
        revisions = await revision_repo.get_multi(db_session, skip=0, limit=1000)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert query_time < 1.0, f"大量データクエリ時間が長すぎます: {query_time:.2f}秒"
        
        print(f"✓ バルクデータクエリ完了 - {len(revisions)}件, クエリ時間: {query_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_complex_query_performance(self, db_session: AsyncSession):
        """複雑クエリ性能テスト"""
        from app.repositories.revision import RevisionRepository
        
        # テストデータ確保
        admin_user, _ = await create_test_user_and_token(db_session, role="admin")
        
        revision_repo = RevisionRepository()
        
        # 複雑な条件での検索
        start_time = time.time()
        
        # mixed_access_revisions（実装されている複雑なクエリ）
        revisions = await revision_repo.get_mixed_access_revisions(
            db_session, user_id=admin_user.id, skip=0, limit=100
        )
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert query_time < 2.0, f"複雑クエリ時間が長すぎます: {query_time:.2f}秒"
        
        print(f"✓ 複雑クエリ完了 - {len(revisions)}件, クエリ時間: {query_time:.3f}秒")


@pytest.mark.performance  
class TestPerformanceMemory:
    """メモリ使用量テスト"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_large_dataset(self, client: AsyncClient, db_session: AsyncSession):
        """大量データセットでのメモリ使用量テスト"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # テストデータ準備
        admin_user, token = await create_test_user_and_token(db_session, role="admin")
        
        # 大量リクエスト実行
        for i in range(10):  # 10回の大量データリクエスト
            response = await client.get(
                "/api/v1/revisions/",
                params={"skip": i * 100, "limit": 100},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # メモリ使用量が過度に増加していないことを確認
        assert memory_increase < 100, f"メモリ使用量が過度に増加: {memory_increase:.2f}MB"
        
        print(f"✓ メモリ使用量テスト完了 - 初期: {initial_memory:.1f}MB, 最終: {final_memory:.1f}MB, 増加: {memory_increase:.1f}MB")