"""インデックス効果のパフォーマンステスト"""

import pytest
import time
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.crud.user import user_crud
from app.schemas.user import UserCreate, PaginationParams
from app.models.user import GroupEnum


class TestIndexPerformance:
    """インデックスパフォーマンステストクラス"""

    @pytest.mark.asyncio
    async def test_index_coverage_verification(self, clean_db_session):
        """作成したインデックスが存在することを確認"""
        
        # 期待するインデックス一覧
        expected_indexes = [
            'idx_users_is_active_true',
            'idx_users_group', 
            'idx_users_created_at_desc',
            'idx_users_active_created_desc'
        ]
        
        query = text("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'users' 
        AND indexname LIKE 'idx_users_%'
        ORDER BY indexname
        """)
        
        result = await clean_db_session.execute(query)
        indexes = [row.indexname for row in result]
        
        # すべての期待するインデックスが存在することを確認
        for expected_index in expected_indexes:
            assert expected_index in indexes, f"インデックス {expected_index} が見つかりません"
        
        print(f"All performance indexes created successfully: {indexes}")

    @pytest.mark.asyncio
    async def test_active_users_query_performance(self, clean_db_session):
        """is_activeインデックスのパフォーマンステスト"""
        
        # テストデータ作成（アクティブユーザーと非アクティブユーザー）
        test_users = []
        for i in range(20):
            user_data = UserCreate(
                username=f'perftest_active_{i}',
                email=f'perftest_active_{i}@example.com',
                password='password123',
                group=GroupEnum.CSC_1,
                is_active=(i % 2 == 0)  # 半分をアクティブ、半分を非アクティブ
            )
            user = await user_crud.create_user(clean_db_session, user_data)
            test_users.append(user)
        
        await clean_db_session.commit()
        
        # アクティブユーザー取得のパフォーマンス測定
        start_time = time.time()
        active_users = await user_crud.get_active_users(clean_db_session)
        execution_time = time.time() - start_time
        
        # パフォーマンス検証
        assert execution_time < 0.5, f"アクティブユーザー取得が遅すぎます: {execution_time:.3f}秒"
        assert len(active_users) >= 10, "アクティブユーザーが期待した数取得できませんでした"
        
        # 結果の正確性確認
        for user in active_users:
            assert user.is_active is True, "非アクティブユーザーが結果に含まれています"
        
        print(f"Active users query performance: {execution_time:.3f}s, {len(active_users)} users")

    @pytest.mark.asyncio
    async def test_group_filter_query_performance(self, clean_db_session):
        """groupインデックスのパフォーマンステスト"""
        
        # 各グループにテストデータ作成
        groups = [GroupEnum.CSC_1, GroupEnum.CSC_2, GroupEnum.CSC_N, GroupEnum.HHD]
        test_users = []
        
        for group in groups:
            for i in range(5):
                user_data = UserCreate(
                    username=f'perftest_group_{group.value}_{i}',
                    email=f'perftest_group_{group.value}_{i}@example.com',
                    password='password123',
                    group=group,
                    is_active=True
                )
                user = await user_crud.create_user(clean_db_session, user_data)
                test_users.append(user)
        
        await clean_db_session.commit()
        
        # 各グループでの検索パフォーマンス測定
        for group in groups:
            start_time = time.time()
            group_users = await user_crud.get_users_by_group(clean_db_session, group)
            execution_time = time.time() - start_time
            
            # パフォーマンス検証
            assert execution_time < 0.3, f"グループ検索が遅すぎます({group.value}): {execution_time:.3f}秒"
            assert len(group_users) >= 5, f"グループ{group.value}のユーザーが期待した数取得できませんでした"
            
            # 結果の正確性確認
            for user in group_users:
                assert user.group == group, f"異なるグループのユーザーが結果に含まれています: {user.group}"
            
            print(f"Group query performance ({group.value}): {execution_time:.3f}s, {len(group_users)} users")

    @pytest.mark.asyncio
    async def test_recent_users_query_performance(self, clean_db_session):
        """created_atインデックスのパフォーマンステスト"""
        
        # タイムスタンプを変えながらテストデータ作成
        test_users = []
        for i in range(15):
            user_data = UserCreate(
                username=f'perftest_recent_{i}',
                email=f'perftest_recent_{i}@example.com',
                password='password123',
                group=GroupEnum.CSC_1,
                is_active=True
            )
            user = await user_crud.create_user(clean_db_session, user_data)
            test_users.append(user)
            
            # 少し時間を置いて作成時刻に差をつける
            await asyncio.sleep(0.01)
        
        await clean_db_session.commit()
        
        # 最新ユーザー取得のパフォーマンス測定
        start_time = time.time()
        recent_users = await user_crud.get_recent_users(clean_db_session, limit=10)
        execution_time = time.time() - start_time
        
        # パフォーマンス検証
        assert execution_time < 0.3, f"最新ユーザー取得が遅すぎます: {execution_time:.3f}秒"
        assert len(recent_users) == 10, "期待した件数の最新ユーザーが取得できませんでした"
        
        # 結果の正確性確認（作成日時順になっているか）
        for i in range(len(recent_users) - 1):
            assert recent_users[i].created_at >= recent_users[i + 1].created_at, \
                "最新ユーザーが正しい順序で取得されていません"
        
        print(f"Recent users query performance: {execution_time:.3f}s, {len(recent_users)} users")

    @pytest.mark.asyncio
    async def test_composite_index_performance(self, clean_db_session):
        """複合インデックス(is_active, created_at)のパフォーマンステスト"""
        
        # アクティブ・非アクティブユーザーを混在で作成
        test_users = []
        for i in range(20):
            user_data = UserCreate(
                username=f'perftest_composite_{i}',
                email=f'perftest_composite_{i}@example.com',
                password='password123',
                group=GroupEnum.CSC_2,
                is_active=(i % 3 != 0)  # 2/3をアクティブ、1/3を非アクティブ
            )
            user = await user_crud.create_user(clean_db_session, user_data)
            test_users.append(user)
            
            await asyncio.sleep(0.01)
        
        await clean_db_session.commit()
        
        # アクティブユーザーの最新取得のパフォーマンス測定
        start_time = time.time()
        recent_active_users = await user_crud.get_recent_users(
            clean_db_session, 
            limit=10, 
            active_only=True
        )
        execution_time = time.time() - start_time
        
        # パフォーマンス検証
        assert execution_time < 0.3, f"アクティブな最新ユーザー取得が遅すぎます: {execution_time:.3f}秒"
        assert len(recent_active_users) == 10, "期待した件数のアクティブな最新ユーザーが取得できませんでした"
        
        # 結果の正確性確認
        for user in recent_active_users:
            assert user.is_active is True, "非アクティブユーザーが結果に含まれています"
        
        # 作成日時順になっているか確認
        for i in range(len(recent_active_users) - 1):
            assert recent_active_users[i].created_at >= recent_active_users[i + 1].created_at, \
                "アクティブな最新ユーザーが正しい順序で取得されていません"
        
        print(f"Composite index performance: {execution_time:.3f}s, {len(recent_active_users)} users")

    @pytest.mark.asyncio
    async def test_pagination_with_indexes_performance(self, clean_db_session):
        """インデックスとページネーションの組み合わせパフォーマンステスト"""
        
        # 大量テストデータ作成
        test_users = []
        for i in range(50):
            user_data = UserCreate(
                username=f'perftest_page_{i:03d}',
                email=f'perftest_page_{i:03d}@example.com',
                password='password123',
                group=GroupEnum.CSC_N,
                is_active=(i % 4 != 0)  # 3/4をアクティブ
            )
            user = await user_crud.create_user(clean_db_session, user_data)
            test_users.append(user)
        
        await clean_db_session.commit()
        
        # ページネーション付きアクティブユーザー取得のパフォーマンス測定
        pagination = PaginationParams(page=2, limit=10)
        start_time = time.time()
        paginated_active_users = await user_crud.get_active_users(
            clean_db_session, 
            pagination=pagination
        )
        execution_time = time.time() - start_time
        
        # パフォーマンス検証
        assert execution_time < 0.4, f"ページネーション付きアクティブユーザー取得が遅すぎます: {execution_time:.3f}秒"
        assert len(paginated_active_users) <= 10, "ページネーション制限が正しく適用されていません"
        
        # 結果の正確性確認
        for user in paginated_active_users:
            assert user.is_active is True, "非アクティブユーザーが結果に含まれています"
        
        print(f"Pagination + index performance: {execution_time:.3f}s, {len(paginated_active_users)} users")

    @pytest.mark.asyncio
    async def test_index_existence_verification(self, clean_db_session):
        """必要なインデックスが実際に存在することを確認"""
        
        # インデックスの存在確認クエリ
        query = text("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'users' 
        AND (
            indexname = 'idx_users_is_active_true' 
            OR indexname = 'idx_users_group'
            OR indexname = 'idx_users_created_at_desc'
            OR indexname = 'idx_users_active_created_desc'
        )
        ORDER BY indexname
        """)
        
        result = await clean_db_session.execute(query)
        indexes = {row.indexname: row.indexdef for row in result}
        
        # 必要なインデックスがすべて存在することを確認
        required_indexes = [
            'idx_users_is_active_true',
            'idx_users_group',
            'idx_users_created_at_desc',
            'idx_users_active_created_desc'
        ]
        
        for index_name in required_indexes:
            assert index_name in indexes, f"Required index {index_name} not found"
            print(f"[OK] Index {index_name} exists: {indexes[index_name]}")
        
        # 部分インデックスの条件確認
        assert "WHERE (is_active = true)" in indexes['idx_users_is_active_true'], \
            "is_active partial index condition missing"
        assert "WHERE (is_active = true)" in indexes['idx_users_active_created_desc'], \
            "composite partial index condition missing"
        
        print("All required indexes exist with correct definitions")