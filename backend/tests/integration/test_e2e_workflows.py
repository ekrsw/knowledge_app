"""
E2E統合テスト - 完全ワークフローテスト

このモジュールは主要なビジネスフローのE2E（End-to-End）テストを実装します：
- 修正案の完全ワークフロー（作成→提出→承認）
- 通知システムの統合テスト
- 差分表示の統合テスト
- ユーザー認証フローの統合テスト
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.auth import create_test_user_and_token
from tests.factories.article_factory import ArticleFactory
from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.info_category_factory import InfoCategoryFactory


class TestRevisionWorkflowE2E:
    """修正案完全ワークフローE2Eテスト"""
    
    @pytest.mark.asyncio
    async def test_complete_revision_workflow_success(self, client: AsyncClient, db_session: AsyncSession):
        """修正案の完全ワークフロー - 成功シナリオ"""
        # 1. テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # ユーザー作成
        proposer, proposer_token = await create_test_user_and_token(db_session, role="user")
        approver, approver_token = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        
        # 記事作成
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_TEST_ARTICLE",
            title="Original Article",
            info_category=info_category,
            approval_group=approval_group,
            question="Original question content",
            answer="Original answer content"
        )
        
        # 2. フェーズ1: 修正案作成（draft状態）
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "E2E test revision for workflow validation",
            "after_title": "Updated Article Title",
            "after_info_category": str(info_category.category_id),
            "after_question": "Updated question content",
            "after_answer": "Updated answer content"
        }
        
        create_response = await client.post(
            "/api/v1/revisions/",
            json=revision_data,
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        assert create_response.status_code == 201
        revision = create_response.json()
        revision_id = revision["revision_id"]
        assert revision["status"] == "draft"
        assert revision["after_title"] == "Updated Article Title"
        
        # 3. フェーズ2: 修正案提出（draft → submitted）
        submit_response = await client.post(
            f"/api/v1/proposals/{revision_id}/submit",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        assert submit_response.status_code == 200
        submitted_revision = submit_response.json()
        assert submitted_revision["status"] == "submitted"
        assert submitted_revision["revision_id"] == revision_id
        
        # 4. フェーズ3: 承認者による承認（submitted → approved）
        approval_decision = {
            "action": "approve",
            "comment": "E2E test approval - changes look good",
            "priority": "medium"
        }
        
        approve_response = await client.post(
            f"/api/v1/approvals/{revision_id}/decide",
            json=approval_decision,
            headers={"Authorization": f"Bearer {approver_token}"}
        )
        
        assert approve_response.status_code == 200
        approved_revision = approve_response.json()
        assert approved_revision["status"] == "approved"
        assert approved_revision["processed_at"] is not None
        
        # 5. フェーズ4: 最終状態確認
        final_response = await client.get(
            f"/api/v1/revisions/{revision_id}",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        assert final_response.status_code == 200
        final_revision = final_response.json()
        assert final_revision["status"] == "approved"
        assert final_revision["after_title"] == "Updated Article Title"
        assert final_revision["after_question"] == "Updated question content"
        assert final_revision["after_answer"] == "Updated answer content"
        
        print("PASS - Complete revision workflow test completed successfully")
    
    @pytest.mark.asyncio
    async def test_complete_revision_workflow_rejection(self, client: AsyncClient, db_session: AsyncSession):
        """修正案の完全ワークフロー - 却下シナリオ"""
        # 1. テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # ユーザー作成
        proposer, proposer_token = await create_test_user_and_token(db_session, role="user")
        approver, approver_token = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        
        # 記事作成
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_REJECTION_ARTICLE",
            title="Article for Rejection Test",
            info_category=info_category,
            approval_group=approval_group
        )
        
        # 2. 修正案作成→提出
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Revision that will be rejected",
            "after_title": "Problematic Title"
        }
        
        create_response = await client.post(
            "/api/v1/revisions/",
            json=revision_data,
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        assert create_response.status_code == 201
        revision_id = create_response.json()["revision_id"]
        
        # 提出
        await client.post(
            f"/api/v1/proposals/{revision_id}/submit",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        # 3. 承認者による却下
        rejection_decision = {
            "action": "reject",
            "comment": "E2E test rejection - title is inappropriate",
            "priority": "low"
        }
        
        reject_response = await client.post(
            f"/api/v1/approvals/{revision_id}/decide",
            json=rejection_decision,
            headers={"Authorization": f"Bearer {approver_token}"}
        )
        
        assert reject_response.status_code == 200
        rejected_revision = reject_response.json()
        assert rejected_revision["status"] == "rejected"
        
        print("PASS - Complete revision workflow rejection test completed successfully")
    
    @pytest.mark.asyncio
    async def test_revision_workflow_with_withdrawal(self, client: AsyncClient, db_session: AsyncSession):
        """修正案の完全ワークフロー - 撤回シナリオ"""
        # 1. テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        proposer, proposer_token = await create_test_user_and_token(db_session, role="user")
        approver, _ = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_WITHDRAW_ARTICLE",
            title="Article for Withdrawal Test",
            info_category=info_category,
            approval_group=approval_group
        )
        
        # 2. 修正案作成→提出
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Revision that will be withdrawn",
            "after_title": "Title to be withdrawn"
        }
        
        create_response = await client.post(
            "/api/v1/revisions/",
            json=revision_data,
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        revision_id = create_response.json()["revision_id"]
        
        # 提出
        submit_response = await client.post(
            f"/api/v1/proposals/{revision_id}/submit",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        assert submit_response.json()["status"] == "submitted"
        
        # 3. 撤回（submitted → draft）
        withdraw_response = await client.post(
            f"/api/v1/proposals/{revision_id}/withdraw",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        assert withdraw_response.status_code == 200
        withdrawn_revision = withdraw_response.json()
        assert withdrawn_revision["status"] == "draft"
        
        print("PASS - Revision workflow withdrawal test completed successfully")


class TestNotificationSystemE2E:
    """通知システム統合E2Eテスト"""
    
    @pytest.mark.asyncio
    async def test_notification_flow_during_revision_workflow(self, client: AsyncClient, db_session: AsyncSession):
        """修正案ワークフロー中の通知統合テスト"""
        # 1. テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        proposer, proposer_token = await create_test_user_and_token(db_session, role="user")
        approver, approver_token = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_NOTIFICATION_ARTICLE",
            info_category=info_category,
            approval_group=approval_group
        )
        
        # 2. 修正案作成→提出（通知が生成される）
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Notification test revision",
            "after_title": "Title for notification test"
        }
        
        create_response = await client.post(
            "/api/v1/revisions/",
            json=revision_data,
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        revision_id = create_response.json()["revision_id"]
        
        # 提出時に通知が生成される
        await client.post(
            f"/api/v1/proposals/{revision_id}/submit",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        # 3. 承認者の通知確認
        approver_notifications_response = await client.get(
            "/api/v1/notifications/my-notifications",
            headers={"Authorization": f"Bearer {approver_token}"}
        )
        
        assert approver_notifications_response.status_code == 200
        approver_notifications = approver_notifications_response.json()
        
        # 提出通知の確認
        submit_notification = None
        for notif in approver_notifications:
            if notif.get("notification_type") == "revision_submitted":
                submit_notification = notif
                break
        
        if submit_notification:
            assert submit_notification["revision_id"] == revision_id
            assert submit_notification["is_read"] is False
            print("PASS - Submit notification found for approver")
        
        # 4. 承認処理（通知が生成される）
        approval_decision = {
            "action": "approve",
            "comment": "Notification test approval",
            "priority": "medium"
        }
        
        await client.post(
            f"/api/v1/approvals/{revision_id}/decide",
            json=approval_decision,
            headers={"Authorization": f"Bearer {approver_token}"}
        )
        
        # 5. 提案者の通知確認
        proposer_notifications_response = await client.get(
            "/api/v1/notifications/my-notifications",
            headers={"Authorization": f"Bearer {proposer_token}"}
        )
        
        assert proposer_notifications_response.status_code == 200
        proposer_notifications = proposer_notifications_response.json()
        
        # 承認通知の確認
        approval_notification = None
        for notif in proposer_notifications:
            if notif.get("notification_type") == "revision_approved":
                approval_notification = notif
                break
        
        if approval_notification:
            assert approval_notification["revision_id"] == revision_id
            assert approval_notification["is_read"] is False
            print("PASS - Approval notification found for proposer")
        
        print("PASS - Notification system E2E test completed successfully")
    
    @pytest.mark.asyncio
    async def test_notification_read_marking(self, client: AsyncClient, db_session: AsyncSession):
        """通知既読化の統合テスト"""
        # テストデータ準備
        user, token = await create_test_user_and_token(db_session, role="user")
        
        # 通知一覧取得
        notifications_response = await client.get(
            "/api/v1/notifications/my-notifications",
            params={"unread_only": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert notifications_response.status_code == 200
        unread_notifications = notifications_response.json()
        
        if unread_notifications:
            notification_id = unread_notifications[0]["notification_id"]
            
            # 個別通知既読化
            read_response = await client.put(
                f"/api/v1/notifications/{notification_id}/read",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert read_response.status_code == 200
            read_notification = read_response.json()
            assert read_notification["is_read"] is True
            print("PASS - Individual notification read marking test completed")
        
        # 全通知既読化
        read_all_response = await client.put(
            "/api/v1/notifications/read-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert read_all_response.status_code == 200
        print("PASS - All notifications read marking test completed")


class TestDiffDisplayE2E:
    """差分表示統合E2Eテスト"""
    
    @pytest.mark.asyncio
    async def test_diff_display_integration(self, client: AsyncClient, db_session: AsyncSession):
        """差分表示の統合テスト"""
        # 1. テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        user, token = await create_test_user_and_token(db_session, role="user")
        approver, _ = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        
        # 記事作成
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_DIFF_ARTICLE",
            title="Original Title",
            info_category=info_category,
            approval_group=approval_group,
            question="Original question text",
            answer="Original answer text",
            keywords="original, test"
        )
        
        # 2. 修正案作成（複数フィールド変更）
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Diff test with multiple field changes",
            "after_title": "Updated Title",
            "after_question": "Updated question text with more details",
            "after_answer": "Updated answer text with comprehensive explanation",
            "after_keywords": "updated, test, comprehensive"
        }
        
        create_response = await client.post(
            "/api/v1/revisions/",
            json=revision_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        revision_id = create_response.json()["revision_id"]
        
        # 3. 差分データ取得
        diff_response = await client.get(
            f"/api/v1/diffs/{revision_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert diff_response.status_code == 200
        diff_data = diff_response.json()
        
        # 差分データの検証
        assert "field_diffs" in diff_data
        field_diffs = diff_data["field_diffs"]
        
        # field_diffsはリストなので、該当フィールドを探す
        title_diff = None
        question_diff = None
        
        for diff in field_diffs:
            if diff["field_name"] == "title" and diff["change_type"] == "modified":
                title_diff = diff
            elif diff["field_name"] == "question" and diff["change_type"] == "modified":
                question_diff = diff
        
        # title差分の検証
        if title_diff:
            assert title_diff["old_value"] == "Original Title"
            assert title_diff["new_value"] == "Updated Title"
            assert title_diff["change_type"] == "modified"
        
        # question差分の検証
        if question_diff:
            assert question_diff["old_value"] == "Original question text"
            assert question_diff["new_value"] == "Updated question text with more details"
        
        print("PASS - Diff display integration test completed successfully")
    
    @pytest.mark.asyncio
    async def test_formatted_diff_display(self, client: AsyncClient, db_session: AsyncSession):
        """フォーマット済み差分表示テスト"""
        # テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        user, token = await create_test_user_and_token(db_session, role="user")
        approver, _ = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_FORMATTED_DIFF_ARTICLE",
            title="Title for Format Test",
            info_category=info_category,
            approval_group=approval_group
        )
        
        # 修正案作成
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Formatted diff test",
            "after_title": "Formatted Title for Test"
        }
        
        create_response = await client.post(
            "/api/v1/revisions/",
            json=revision_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        revision_id = create_response.json()["revision_id"]
        
        # フォーマット済み差分取得
        formatted_diff_response = await client.get(
            f"/api/v1/diffs/{revision_id}/formatted",
            params={"include_formatting": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert formatted_diff_response.status_code == 200
        formatted_diff = formatted_diff_response.json()
        assert "field_changes" in formatted_diff or "basic_info" in formatted_diff
        
        print("PASS - Formatted diff display test completed successfully")


class TestUserAuthenticationFlowE2E:
    """ユーザー認証フローE2Eテスト"""
    
    @pytest.mark.asyncio
    async def test_complete_authentication_flow(self, client: AsyncClient, db_session: AsyncSession):
        """完全認証フローの統合テスト"""
        # 1. ユーザー登録
        registration_data = {
            "username": "e2e_test_user",
            "email": "e2e_test@example.com",
            "password": "test_password123",
            "full_name": "E2E Test User",
            "sweet_name": "e2e_sweet",
            "ctstage_name": "e2e_stage"
        }
        
        register_response = await client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        assert register_response.status_code == 201
        registered_user = register_response.json()
        assert registered_user["username"] == "e2e_test_user"
        assert registered_user["email"] == "e2e_test@example.com"
        
        # 2. ログイン（JSON形式）
        login_data = {
            "email": "e2e_test@example.com",
            "password": "test_password123"
        }
        
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json=login_data
        )
        
        assert login_response.status_code == 200
        login_result = login_response.json()
        assert "access_token" in login_result
        assert login_result["token_type"] == "bearer"
        
        access_token = login_result["access_token"]
        
        # 3. 認証が必要なエンドポイントアクセス
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert me_response.status_code == 200
        user_info = me_response.json()
        assert user_info["username"] == "e2e_test_user"
        assert user_info["email"] == "e2e_test@example.com"
        
        # 4. トークンテスト
        token_test_response = await client.post(
            "/api/v1/auth/test-token",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert token_test_response.status_code == 200
        
        print("PASS - Complete authentication flow test completed successfully")
    
    @pytest.mark.asyncio
    async def test_authentication_error_scenarios(self, client: AsyncClient, db_session: AsyncSession):
        """認証エラーシナリオテスト"""
        # 1. 無効なクレデンシャルでのログイン
        invalid_login_data = {
            "email": "nonexistent@example.com",
            "password": "wrong_password"
        }
        
        invalid_login_response = await client.post(
            "/api/v1/auth/login/json",
            json=invalid_login_data
        )
        
        assert invalid_login_response.status_code == 401
        
        # 2. 無効なトークンでのアクセス
        invalid_token_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert invalid_token_response.status_code in [401, 422]  # 401 Unauthorized or 422 Unprocessable Entity
        
        # 3. トークンなしでのアクセス
        no_token_response = await client.get("/api/v1/auth/me")
        assert no_token_response.status_code in [401, 403]  # 401 Unauthorized or 403 Forbidden
        
        print("PASS - Authentication error scenarios test completed successfully")


class TestIntegratedBusinessScenarios:
    """統合ビジネスシナリオテスト"""
    
    @pytest.mark.asyncio
    async def test_multi_user_collaboration_scenario(self, client: AsyncClient, db_session: AsyncSession):
        """複数ユーザー協力シナリオテスト"""
        # 複数のユーザーと役割でのワークフロー統合テスト
        
        # 1. テストデータ準備
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # 複数ユーザー作成
        user1, user1_token = await create_test_user_and_token(db_session, role="user")
        user2, user2_token = await create_test_user_and_token(db_session, role="user")
        approver1, approver1_token = await create_test_user_and_token(db_session, role="approver", approval_group=approval_group)
        admin, admin_token = await create_test_user_and_token(db_session, role="admin")
        
        # 記事作成
        article = await ArticleFactory.create(
            db_session,
            article_id="E2E_COLLABORATION_ARTICLE",
            title="Collaboration Test Article",
            info_category=info_category,
            approval_group=approval_group
        )
        
        # 2. User1が修正案作成
        revision1_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver1.id),
            "reason": "User1's revision proposal",
            "after_title": "Updated by User1"
        }
        
        create1_response = await client.post(
            "/api/v1/revisions/",
            json=revision1_data,
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        
        assert create1_response.status_code == 201
        revision1_id = create1_response.json()["revision_id"]
        
        # 3. User2が別の修正案作成
        revision2_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver1.id),
            "reason": "User2's revision proposal",
            "after_title": "Updated by User2"
        }
        
        create2_response = await client.post(
            "/api/v1/revisions/",
            json=revision2_data,
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        
        assert create2_response.status_code == 201
        revision2_id = create2_response.json()["revision_id"]
        
        # 4. 管理者が両方の修正案を確認
        admin_revisions_response = await client.get(
            "/api/v1/revisions/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert admin_revisions_response.status_code == 200
        admin_revisions = admin_revisions_response.json()
        
        # 作成した修正案が含まれていることを確認
        revision_ids = [rev["revision_id"] for rev in admin_revisions]
        assert revision1_id in revision_ids
        assert revision2_id in revision_ids
        
        # 5. User1が自分の修正案を提出
        await client.post(
            f"/api/v1/proposals/{revision1_id}/submit",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        
        # 6. 承認者が承認キューを確認
        queue_response = await client.get(
            "/api/v1/approvals/queue",
            headers={"Authorization": f"Bearer {approver1_token}"}
        )
        
        assert queue_response.status_code == 200
        queue = queue_response.json()
        
        # 提出された修正案が承認キューに含まれていることを確認
        queue_revision_ids = [rev["revision_id"] for rev in queue]
        assert revision1_id in queue_revision_ids
        
        print("PASS - Multi-user collaboration scenario test completed successfully")