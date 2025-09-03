"""
Approval Management API Integration Tests

Tests for /api/v1/approvals endpoints including permission controls,
approval decisions, queue management, and workload analysis.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.revision_factory import RevisionFactory
from tests.factories.article_factory import ArticleFactory
from tests.factories.info_category_factory import InfoCategoryFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


class TestApprovalDecision:
    """Test approval decision processing endpoint (POST /api/v1/approvals/{revision_id}/decide)"""
    
    async def test_approve_revision_as_designated_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test approving revision as the designated approver"""
        # Create test entities
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Create users
        proposer = await UserFactory.create_user(db_session, username="proposer", email="proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver", email="approver@example.com")
        
        # Create article and revision
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=approver,
            target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "approver@example.com", "password": "testpassword123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Process approval decision
        decision_data = {
            "action": "approve",
            "comment": "Looks good, approved!",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "approved"
        assert result["revision_id"] == str(revision.revision_id)
    
    async def test_reject_revision_as_designated_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test rejecting revision as the designated approver"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="proposer2", email="proposer2@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver2", email="approver2@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=approver,
            target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "approver2@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Process rejection decision
        decision_data = {
            "action": "reject",
            "comment": "Needs more information",
            "priority": "high"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "rejected"
    
    async def test_approval_decision_permission_denied_wrong_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test approval decision denied for wrong approver"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="proposer3", email="proposer3@example.com")
        designated_approver = await UserFactory.create_approver(db_session, approval_group, username="approver3", email="approver3@example.com")
        other_approver = await UserFactory.create_approver(db_session, approval_group, username="other_approver", email="other_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=designated_approver,  # Designated approver
            target_article_id=article.article_id
        )
        
        # Login as OTHER approver (not designated)
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "other_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to process approval (should fail)
        decision_data = {
            "action": "approve",
            "comment": "I want to approve this",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "approver" in response.json()["detail"].lower()
    
    async def test_approval_decision_permission_denied_regular_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test approval decision denied for regular user"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="proposer4", email="proposer4@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver4", email="approver4@example.com")
        regular_user = await UserFactory.create_user(db_session, username="regular", email="regular@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=approver,
            target_article_id=article.article_id
        )
        
        # Login as regular user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "regular@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to process approval (should fail due to insufficient role)
        decision_data = {
            "action": "approve",
            "comment": "I'm not an approver",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_approval_decision_admin_can_approve_any(self, client: AsyncClient, db_session: AsyncSession):
        """Test admin can approve any revision regardless of designated approver"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="proposer5", email="proposer5@example.com")
        designated_approver = await UserFactory.create_approver(db_session, approval_group, username="approver5", email="approver5@example.com")
        admin = await UserFactory.create_admin(db_session, username="admin", email="admin@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=designated_approver,
            target_article_id=article.article_id
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "admin@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Admin can approve even if not designated approver
        decision_data = {
            "action": "approve",
            "comment": "Admin override approval",
            "priority": "urgent"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "approved"
    
    async def test_approval_decision_nonexistent_revision(self, client: AsyncClient, test_users):
        """Test approval decision for non-existent revision"""
        # Login as admin
        admin = test_users["admin"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": admin.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to approve non-existent revision
        fake_revision_id = str(uuid4())
        decision_data = {
            "action": "approve",
            "comment": "Non-existent revision",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{fake_revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_approval_decision_draft_status_error(self, client: AsyncClient, db_session: AsyncSession):
        """Test approval decision fails for revision in draft status"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="proposer6", email="proposer6@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver6", email="approver6@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(  # Draft status
            db_session,
            proposer=proposer,
            approver=approver,
            target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "approver6@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to approve draft revision (should fail)
        decision_data = {
            "action": "approve",
            "comment": "Cannot approve draft",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "status" in response.json()["detail"].lower()
    
    async def test_approval_decision_invalid_action(self, client: AsyncClient, db_session: AsyncSession):
        """Test approval decision with invalid action value"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="proposer7", email="proposer7@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver7", email="approver7@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=approver,
            target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "approver7@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Invalid action value
        decision_data = {
            "action": "invalid_action",
            "comment": "Invalid action test",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error


class TestApprovalQueue:
    """Test approval queue endpoint (GET /api/v1/approvals/queue)"""
    
    async def test_get_approval_queue_as_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting approval queue as approver"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Create approver
        approver = await UserFactory.create_approver(db_session, approval_group, username="queue_approver", email="queue_approver@example.com")
        
        # Create multiple revisions for articles in this approval group
        proposers = []
        revisions = []
        for i in range(3):
            proposer = await UserFactory.create_user(
                db_session, 
                username=f"queue_proposer{i}", 
                email=f"queue_proposer{i}@example.com"
            )
            proposers.append(proposer)
            
            article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
            revision = await RevisionFactory.create_submitted(
                db_session,
                proposer=proposer,
                approver=approver,  # This will set approver_id for designated approver logic
                target_article_id=article.article_id
            )
            revisions.append(revision)
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "queue_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get approval queue
        response = await client.get("/api/v1/approvals/queue", headers=headers)
        
        assert response.status_code == 200
        queue_data = response.json()
        assert isinstance(queue_data, list)
        assert len(queue_data) == 3
        
        # Verify queue item structure
        for item in queue_data:
            assert "revision_id" in item
            assert "article_number" in item  # Should include article_number
            assert "proposer_name" in item
            assert "submitted_at" in item
            assert "priority" in item
            assert "impact_level" in item
            assert "reason" in item
    
    async def test_get_approval_queue_with_priority_filter(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting approval queue with priority filter"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        approver = await UserFactory.create_approver(db_session, approval_group, username="priority_approver", email="priority_approver@example.com")
        
        # Create revisions with different priorities (this would be set through the decision system)
        proposer = await UserFactory.create_user(db_session, username="priority_proposer", email="priority_proposer@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session,
            proposer=proposer,
            approver=approver,
            target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "priority_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test priority filter
        response = await client.get("/api/v1/approvals/queue?priority=high", headers=headers)
        assert response.status_code == 200
        
        # Test invalid priority filter
        response = await client.get("/api/v1/approvals/queue?priority=invalid", headers=headers)
        assert response.status_code == 422  # Validation error
    
    async def test_get_approval_queue_with_limit(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting approval queue with limit parameter"""
        # Create test setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        approver = await UserFactory.create_approver(db_session, approval_group, username="limit_approver", email="limit_approver@example.com")
        
        # Create more revisions than the limit
        for i in range(5):
            proposer = await UserFactory.create_user(
                db_session, 
                username=f"limit_proposer{i}", 
                email=f"limit_proposer{i}@example.com"
            )
            article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
            await RevisionFactory.create_submitted(
                db_session,
                proposer=proposer,
                approver=approver,
                target_article_id=article.article_id
            )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "limit_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test limit parameter
        response = await client.get("/api/v1/approvals/queue?limit=3", headers=headers)
        assert response.status_code == 200
        queue_data = response.json()
        assert len(queue_data) <= 3
        
        # Test limit exceeding maximum
        response = await client.get("/api/v1/approvals/queue?limit=200", headers=headers)
        assert response.status_code == 422  # Should fail validation (max 100)
    
    async def test_get_approval_queue_permission_denied_regular_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test approval queue access denied for regular user"""
        # Create regular user
        regular_user = await UserFactory.create_user(db_session, username="queue_regular", email="queue_regular@example.com")
        
        # Login as regular user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "queue_regular@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access approval queue (should fail)
        response = await client.get("/api/v1/approvals/queue", headers=headers)
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_get_approval_queue_empty_queue(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting approval queue when no revisions are pending"""
        # Create approver
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group, username="empty_approver", email="empty_approver@example.com")
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "empty_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get approval queue (should be empty)
        response = await client.get("/api/v1/approvals/queue", headers=headers)
        
        assert response.status_code == 200
        queue_data = response.json()
        assert isinstance(queue_data, list)
        assert len(queue_data) == 0


class TestApprovalWorkload:
    """Test approval workload endpoints"""
    
    async def test_get_own_workload_as_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting own workload information as approver"""
        # Create approver
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group, username="workload_approver", email="workload_approver@example.com")
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "workload_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get workload
        response = await client.get("/api/v1/approvals/workload", headers=headers)
        
        assert response.status_code == 200
        workload_data = response.json()
        
        # Verify workload data structure
        assert "approver_id" in workload_data
        assert "pending_count" in workload_data
        assert "average_review_time" in workload_data
        assert "current_capacity" in workload_data
        assert workload_data["approver_id"] == str(approver.id)
    
    async def test_get_specific_approver_workload_as_admin(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting specific approver's workload as admin"""
        # Create approver and admin
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        approver = await UserFactory.create_approver(db_session, approval_group, username="target_approver", email="target_approver@example.com")
        admin = await UserFactory.create_admin(db_session, username="workload_admin", email="workload_admin@example.com")
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "workload_admin@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get specific approver's workload
        response = await client.get(f"/api/v1/approvals/workload/{approver.id}", headers=headers)
        
        assert response.status_code == 200
        workload_data = response.json()
        assert workload_data["approver_id"] == str(approver.id)
    
    async def test_get_specific_approver_workload_permission_denied_non_admin(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting specific approver's workload denied for non-admin"""
        # Create approvers
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        approver1 = await UserFactory.create_approver(db_session, approval_group, username="approver1", email="approver1@example.com")
        approver2 = await UserFactory.create_approver(db_session, approval_group, username="approver2", email="approver2@example.com")
        
        # Login as approver1
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "approver1@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get approver2's workload (should fail)
        response = await client.get(f"/api/v1/approvals/workload/{approver2.id}", headers=headers)
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_get_workload_nonexistent_approver(self, client: AsyncClient, test_users):
        """Test getting workload for non-existent approver"""
        # Login as admin
        admin = test_users["admin"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": admin.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get workload for non-existent approver
        fake_approver_id = str(uuid4())
        response = await client.get(f"/api/v1/approvals/workload/{fake_approver_id}", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestApprovalPermissionMatrix:
    """Test comprehensive permission matrix for approval endpoints"""
    
    @pytest.mark.parametrize("role,endpoint,expected_status", [
        # Approval decision endpoint
        ("admin", "/api/v1/approvals/{revision_id}/decide", [200, 400, 404]),
        ("approver", "/api/v1/approvals/{revision_id}/decide", [200, 400, 404]),
        ("user", "/api/v1/approvals/{revision_id}/decide", 403),
        
        # Approval queue endpoint
        ("admin", "/api/v1/approvals/queue", 200),
        ("approver", "/api/v1/approvals/queue", 200),
        ("user", "/api/v1/approvals/queue", 403),
        
        # Own workload endpoint
        ("admin", "/api/v1/approvals/workload", 200),
        ("approver", "/api/v1/approvals/workload", 200),
        ("user", "/api/v1/approvals/workload", 403),
        
        # Specific workload endpoint (admin only)
        ("admin", "/api/v1/approvals/workload/{approver_id}", [200, 404]),
        ("approver", "/api/v1/approvals/workload/{approver_id}", 403),
        ("user", "/api/v1/approvals/workload/{approver_id}", 403),
    ])
    async def test_approval_permission_matrix(self, client: AsyncClient, test_users, db_session: AsyncSession, 
                                            role, endpoint, expected_status):
        """Test role-based access control for approval endpoints"""
        # Get user for the specified role
        user = test_users[role]
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": user.email, "password": "testpassword123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create test revision if needed for decision endpoint
        if "{revision_id}" in endpoint:
            approval_group = await ApprovalGroupFactory.create_development_group(db_session)
            info_category = await InfoCategoryFactory.create_technology_category(db_session)
            
            proposer = await UserFactory.create_user(
                db_session, 
                username="matrix_proposer", 
                email="matrix_proposer@example.com"
            )
            approver = await UserFactory.create_approver(
                db_session, 
                approval_group, 
                username="matrix_approver", 
                email="matrix_approver@example.com"
            )
            
            article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
            revision = await RevisionFactory.create_submitted(
                db_session,
                proposer=proposer,
                approver=approver,
                target_article_id=article.article_id
            )
            
            endpoint = endpoint.replace("{revision_id}", str(revision.revision_id))
        
        # Replace approver_id with actual approver ID
        if "{approver_id}" in endpoint:
            endpoint = endpoint.replace("{approver_id}", str(test_users["approver"].id))
        
        # Make request based on endpoint
        if endpoint.endswith("/decide"):
            # POST request for decision
            decision_data = {
                "action": "approve",
                "comment": "Test decision",
                "priority": "medium"
            }
            response = await client.post(endpoint, json=decision_data, headers=headers)
        else:
            # GET request for other endpoints
            response = await client.get(endpoint, headers=headers)
        
        # Check expected status
        if isinstance(expected_status, list):
            assert response.status_code in expected_status
        else:
            assert response.status_code == expected_status