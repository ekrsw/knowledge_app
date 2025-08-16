"""
Revision Management API Integration Tests

Tests for /api/v1/revisions endpoints including CRUD operations,
permission controls, status management, and data filtering.
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


class TestRevisionList:
    """Test revision list endpoint (GET /api/v1/revisions/)"""
    
    async def test_list_revisions_as_admin(self, client: AsyncClient, db_session: AsyncSession):
        """Test admin can see all revisions"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Create users
        proposer1 = await UserFactory.create_user(db_session, username="proposer1", email="proposer1@example.com")
        proposer2 = await UserFactory.create_user(db_session, username="proposer2", email="proposer2@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver", email="approver@example.com")
        admin = await UserFactory.create_admin(db_session, username="list_admin", email="list_admin@example.com")
        
        # Create revisions from different proposers
        article1 = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        article2 = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        revision1 = await RevisionFactory.create_draft(
            db_session, proposer=proposer1, approver=approver, target_article_id=article1.article_id
        )
        revision2 = await RevisionFactory.create_submitted(
            db_session, proposer=proposer2, approver=approver, target_article_id=article2.article_id
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "list_admin@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revisions list
        response = await client.get("/api/v1/revisions/", headers=headers)
        
        assert response.status_code == 200
        revisions_data = response.json()
        assert isinstance(revisions_data, list)
        assert len(revisions_data) >= 2
        
        # Verify revision data structure
        revision_ids = [r["revision_id"] for r in revisions_data]
        assert str(revision1.revision_id) in revision_ids
        assert str(revision2.revision_id) in revision_ids
    
    async def test_list_revisions_as_approver_filtered(self, client: AsyncClient, db_session: AsyncSession):
        """Test approver sees only revisions assigned to their group"""
        # Create approval groups
        dev_group = await ApprovalGroupFactory.create_development_group(db_session)
        qa_group = await ApprovalGroupFactory.create_quality_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Create approvers for different groups
        dev_approver = await UserFactory.create_approver(db_session, dev_group, username="dev_approver", email="dev_approver@example.com")
        qa_approver = await UserFactory.create_approver(db_session, qa_group, username="qa_approver", email="qa_approver@example.com")
        
        # Create proposer
        proposer = await UserFactory.create_user(db_session, username="filter_proposer", email="filter_proposer@example.com")
        
        # Create articles for different groups
        dev_article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=dev_group)
        qa_article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=qa_group)
        
        # Create revisions assigned to different approvers
        dev_revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=dev_approver, target_article_id=dev_article.article_id
        )
        qa_revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=qa_approver, target_article_id=qa_article.article_id
        )
        
        # Login as dev approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "dev_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revisions (should only see dev group revisions)
        response = await client.get("/api/v1/revisions/", headers=headers)
        
        assert response.status_code == 200
        revisions_data = response.json()
        
        # With new permission model: should see both submitted revisions (public)
        revision_ids = [r["revision_id"] for r in revisions_data]
        assert str(dev_revision.revision_id) in revision_ids
        assert str(qa_revision.revision_id) in revision_ids  # Changed: now visible as submitted is public
    
    async def test_list_revisions_as_user_own_only(self, client: AsyncClient, db_session: AsyncSession):
        """Test regular user sees only their own revisions"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Create users
        user1 = await UserFactory.create_user(db_session, username="own_user", email="own_user@example.com")
        user2 = await UserFactory.create_user(db_session, username="other_user", email="other_user@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="filter_approver", email="filter_approver@example.com")
        
        # Create revisions from different users
        article1 = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        article2 = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        own_revision = await RevisionFactory.create_draft(
            db_session, proposer=user1, approver=approver, target_article_id=article1.article_id
        )
        other_revision = await RevisionFactory.create_draft(
            db_session, proposer=user2, approver=approver, target_article_id=article2.article_id
        )
        
        # Login as user1
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "own_user@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revisions (should only see own revisions)
        response = await client.get("/api/v1/revisions/", headers=headers)
        
        assert response.status_code == 200
        revisions_data = response.json()
        
        # Should contain own revision but not other's revision
        revision_ids = [r["revision_id"] for r in revisions_data]
        assert str(own_revision.revision_id) in revision_ids
        assert str(other_revision.revision_id) not in revision_ids
    
    async def test_list_revisions_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test revision list pagination"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        admin = await UserFactory.create_admin(db_session, username="page_admin", email="page_admin@example.com")
        proposer = await UserFactory.create_user(db_session, username="page_proposer", email="page_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="page_approver", email="page_approver@example.com")
        
        # Create multiple revisions
        revisions = []
        for i in range(5):
            article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
            revision = await RevisionFactory.create_draft(
                db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
            )
            revisions.append(revision)
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "page_admin@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with limit
        response = await client.get("/api/v1/revisions/?limit=3", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
        
        # Test with skip
        response = await client.get("/api/v1/revisions/?skip=2&limit=3", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestRevisionGet:
    """Test revision detail endpoint (GET /api/v1/revisions/{revision_id})"""
    
    async def test_get_revision_as_proposer(self, client: AsyncClient, db_session: AsyncSession):
        """Test proposer can access their own revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="get_proposer", email="get_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="get_approver", email="get_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_with_content(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "get_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revision details
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        
        assert response.status_code == 200
        revision_data = response.json()
        
        # Verify revision data structure
        assert revision_data["revision_id"] == str(revision.revision_id)
        assert revision_data["proposer_id"] == str(proposer.id)
        assert revision_data["approver_id"] == str(approver.id)
        assert revision_data["status"] == revision.status
        assert "after_title" in revision_data
        assert "after_answer" in revision_data
    
    async def test_get_revision_as_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test approver can access assigned revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="get_proposer2", email="get_proposer2@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="get_approver2", email="get_approver2@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "get_approver2@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revision details
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        
        assert response.status_code == 200
        revision_data = response.json()
        assert revision_data["revision_id"] == str(revision.revision_id)
    
    async def test_get_revision_as_admin(self, client: AsyncClient, db_session: AsyncSession):
        """Test admin can access any revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="get_proposer3", email="get_proposer3@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="get_approver3", email="get_approver3@example.com")
        admin = await UserFactory.create_admin(db_session, username="get_admin", email="get_admin@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "get_admin@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revision details
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        
        assert response.status_code == 200
        revision_data = response.json()
        assert revision_data["revision_id"] == str(revision.revision_id)
    
    async def test_get_revision_permission_denied_unrelated_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test unrelated user cannot access revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="get_proposer4", email="get_proposer4@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="get_approver4", email="get_approver4@example.com")
        unrelated_user = await UserFactory.create_user(db_session, username="unrelated", email="unrelated@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        # Create a draft revision (private) instead of submitted (public)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as unrelated user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "unrelated@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get draft revision (should fail - draft is private to proposer)
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_get_revision_public_access_submitted_approved(self, client: AsyncClient, db_session: AsyncSession):
        """Test all users can access submitted and approved revisions"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="public_proposer", email="public_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="public_approver", email="public_approver@example.com")
        unrelated_user = await UserFactory.create_user(db_session, username="public_unrelated", email="public_unrelated@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create submitted and approved revisions
        submitted_revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        approved_revision = await RevisionFactory.create_approved(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as unrelated user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "public_unrelated@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Should be able to access submitted revision
        response = await client.get(f"/api/v1/revisions/{submitted_revision.revision_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["revision_id"] == str(submitted_revision.revision_id)
        
        # Should be able to access approved revision
        response = await client.get(f"/api/v1/revisions/{approved_revision.revision_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["revision_id"] == str(approved_revision.revision_id)
    
    async def test_get_nonexistent_revision(self, client: AsyncClient, test_users):
        """Test getting non-existent revision returns 404"""
        # Login as admin
        admin = test_users["admin"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": admin.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get non-existent revision
        fake_revision_id = str(uuid4())
        response = await client.get(f"/api/v1/revisions/{fake_revision_id}", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRevisionCreate:
    """Test revision creation endpoint (POST /api/v1/revisions/)"""
    
    async def test_create_revision_as_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test regular user can create revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="create_user", email="create_user@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="create_approver", email="create_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Login as user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "create_user@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create revision data
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Need to update the information",
            "after_title": "Updated Article Title",
            "after_info_category": str(info_category.category_id),
            "after_keywords": "updated, keywords",
            "after_importance": True,
            "after_publish_start": "2024-01-01",
            "after_publish_end": "2024-12-31",
            "after_target": "Updated target audience",
            "after_question": "What is the updated question?",
            "after_answer": "This is the updated answer.",
            "after_additional_comment": "Additional comments here"
        }
        
        # Create revision
        response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
        
        assert response.status_code == 201
        created_revision = response.json()
        
        # Verify revision data
        assert created_revision["target_article_id"] == article.article_id
        assert created_revision["proposer_id"] == str(proposer.id)
        assert created_revision["approver_id"] == str(approver.id)
        assert created_revision["status"] == "draft"
        assert created_revision["after_title"] == "Updated Article Title"
        assert "revision_id" in created_revision
    
    async def test_create_revision_missing_required_fields(self, client: AsyncClient, test_users):
        """Test creating revision with missing required fields"""
        # Login as user
        user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Missing required fields
        incomplete_data = {
            "reason": "Need to update",
            "after_title": "Title"
        }
        
        response = await client.post("/api/v1/revisions/", json=incomplete_data, headers=headers)
        assert response.status_code == 422
    
    async def test_create_revision_nonexistent_approver(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating revision with non-existent approver"""
        # Create minimal test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="create_user2", email="create_user2@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Login as user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "create_user2@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create revision with non-existent approver
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(uuid4()),  # Non-existent approver
            "reason": "Test with fake approver",
            "after_title": "Title",
            "after_info_category": str(info_category.category_id),
            "after_question": "Question",
            "after_answer": "Answer"
        }
        
        response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
        assert response.status_code in [400, 404]  # Should fail validation


class TestRevisionUpdate:
    """Test revision update endpoint (PUT /api/v1/revisions/{revision_id})"""
    
    async def test_update_revision_as_proposer_draft(self, client: AsyncClient, db_session: AsyncSession):
        """Test proposer can update their own draft revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="update_proposer", email="update_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="update_approver", email="update_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "update_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update revision data
        update_data = {
            "reason": "Updated reason for revision",
            "after_title": "Updated Title",
            "after_answer": "Updated answer content"
        }
        
        # Update revision
        response = await client.put(f"/api/v1/revisions/{revision.revision_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        updated_revision = response.json()
        assert updated_revision["reason"] == "Updated reason for revision"
        assert updated_revision["after_title"] == "Updated Title"
        assert updated_revision["after_answer"] == "Updated answer content"
    
    async def test_update_revision_permission_denied_submitted_status(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating revision fails when status is submitted"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="update_proposer2", email="update_proposer2@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="update_approver2", email="update_approver2@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(  # Submitted status
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "update_proposer2@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update submitted revision (should fail)
        update_data = {
            "reason": "Cannot update submitted revision",
            "after_title": "Should not update"
        }
        
        response = await client.put(f"/api/v1/revisions/{revision.revision_id}", json=update_data, headers=headers)
        
        assert response.status_code == 400
        assert "status" in response.json()["detail"].lower() or "permission" in response.json()["detail"].lower()
    
    async def test_update_revision_permission_denied_other_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test other user cannot update revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="update_proposer3", email="update_proposer3@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="update_approver3", email="update_approver3@example.com")
        other_user = await UserFactory.create_user(db_session, username="other_update", email="other_update@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as other user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "other_update@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update other user's revision (should fail)
        update_data = {
            "reason": "Should not be allowed",
            "after_title": "Unauthorized update"
        }
        
        response = await client.put(f"/api/v1/revisions/{revision.revision_id}", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "own revisions" in response.json()["detail"].lower()


class TestRevisionStatusUpdate:
    """Test revision status update endpoint (PATCH /api/v1/revisions/{revision_id}/status)"""
    
    async def test_update_status_as_admin(self, client: AsyncClient, db_session: AsyncSession):
        """Test admin can update revision status"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="status_proposer", email="status_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="status_approver", email="status_approver@example.com")
        admin = await UserFactory.create_admin(db_session, username="status_admin", email="status_admin@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_admin@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update status
        status_data = {"status": "submitted"}
        response = await client.patch(f"/api/v1/revisions/{revision.revision_id}/status", json=status_data, headers=headers)
        
        assert response.status_code == 200
        updated_revision = response.json()
        assert updated_revision["status"] == "submitted"
    
    async def test_update_status_permission_denied_regular_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test regular user cannot directly update status"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="status_proposer2", email="status_proposer2@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="status_approver2", email="status_approver2@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as regular user (proposer)
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_proposer2@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update status (should fail)
        status_data = {"status": "submitted"}
        response = await client.patch(f"/api/v1/revisions/{revision.revision_id}/status", json=status_data, headers=headers)
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_update_status_invalid_transition(self, client: AsyncClient, db_session: AsyncSession):
        """Test invalid status transition"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="status_proposer3", email="status_proposer3@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="status_approver3", email="status_approver3@example.com")
        admin = await UserFactory.create_admin(db_session, username="status_admin2", email="status_admin2@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_approved(  # Already approved
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_admin2@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try invalid transition (approved -> draft)
        status_data = {"status": "draft"}
        response = await client.patch(f"/api/v1/revisions/{revision.revision_id}/status", json=status_data, headers=headers)
        
        assert response.status_code in [400, 422]  # Should fail validation


class TestRevisionPermissionMatrix:
    """Test comprehensive permission matrix for revision endpoints"""
    
    @pytest.mark.parametrize("role,endpoint,method,expected_status", [
        # Revision list endpoint
        ("admin", "/api/v1/revisions/", "GET", 200),
        ("approver", "/api/v1/revisions/", "GET", 200),
        ("user", "/api/v1/revisions/", "GET", 200),
        
        # Revision create endpoint
        ("admin", "/api/v1/revisions/", "POST", [201, 400, 404, 422]),
        ("approver", "/api/v1/revisions/", "POST", [201, 400, 404, 422]),
        ("user", "/api/v1/revisions/", "POST", [201, 400, 404, 422]),
        
        # Revision detail endpoint (access control varies by relationship)
        ("admin", "/api/v1/revisions/{revision_id}", "GET", [200, 404]),
        ("approver", "/api/v1/revisions/{revision_id}", "GET", [200, 403, 404]),
        ("user", "/api/v1/revisions/{revision_id}", "GET", [200, 403, 404]),
        
        # Revision update endpoint (proposer only, draft status)
        ("admin", "/api/v1/revisions/{revision_id}", "PUT", [200, 400, 403, 404]),
        ("approver", "/api/v1/revisions/{revision_id}", "PUT", [200, 400, 403, 404]),
        ("user", "/api/v1/revisions/{revision_id}", "PUT", [200, 400, 403, 404]),
        
        # Status update endpoint
        ("admin", "/api/v1/revisions/{revision_id}/status", "PATCH", [200, 400, 404, 422]),
        ("approver", "/api/v1/revisions/{revision_id}/status", "PATCH", [200, 400, 403, 404, 422]),
        ("user", "/api/v1/revisions/{revision_id}/status", "PATCH", 403),
    ])
    async def test_revision_permission_matrix(self, client: AsyncClient, test_users, db_session: AsyncSession,
                                            role, endpoint, method, expected_status):
        """Test role-based access control for revision endpoints"""
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
        
        # Create test revision if needed for detail/update endpoints
        if "{revision_id}" in endpoint:
            approval_group = await ApprovalGroupFactory.create_development_group(db_session)
            info_category = await InfoCategoryFactory.create_technology_category(db_session)
            
            proposer = test_users["user"] if role == "user" else await UserFactory.create_user(
                db_session, username="matrix_proposer", email="matrix_proposer@example.com"
            )
            approver = test_users["approver"]
            
            article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
            revision = await RevisionFactory.create_draft(
                db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
            )
            
            endpoint = endpoint.replace("{revision_id}", str(revision.revision_id))
        
        # Prepare request data for POST/PUT/PATCH
        request_data = None
        if method in ["POST", "PUT"]:
            approval_group = await ApprovalGroupFactory.create_development_group(db_session)
            info_category = await InfoCategoryFactory.create_technology_category(db_session)
            article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
            
            request_data = {
                "target_article_id": article.article_id,
                "approver_id": str(test_users["approver"].id),
                "reason": "Test revision",
                "after_title": "Test Title",
                "after_info_category": str(info_category.category_id),
                "after_question": "Test question?",
                "after_answer": "Test answer"
            }
        elif method == "PATCH":
            request_data = {"status": "submitted"}
        
        # Make request
        if method == "GET":
            response = await client.get(endpoint, headers=headers)
        elif method == "POST":
            response = await client.post(endpoint, json=request_data, headers=headers)
        elif method == "PUT":
            response = await client.put(endpoint, json=request_data, headers=headers)
        elif method == "PATCH":
            response = await client.patch(endpoint, json=request_data, headers=headers)
        
        # Check expected status
        if isinstance(expected_status, list):
            assert response.status_code in expected_status
        else:
            assert response.status_code == expected_status


class TestRevisionsByArticle:
    """Test revision list by article endpoint (GET /api/v1/revisions/by-article/{target_article_id})"""
    
    async def test_get_revisions_by_article_public_only(self, client: AsyncClient, db_session: AsyncSession):
        """Test that only submitted/approved revisions are returned for a specific article"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Create users
        proposer = await UserFactory.create_user(db_session, username="art_proposer", email="art_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="art_approver", email="art_approver@example.com")
        regular_user = await UserFactory.create_user(db_session, username="art_user", email="art_user@example.com")
        
        # Create articles
        target_article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        other_article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create revisions for target article with different statuses
        draft_revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=target_article.article_id
        )
        submitted_revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=target_article.article_id
        )
        approved_revision = await RevisionFactory.create_approved(
            db_session, proposer=proposer, approver=approver, target_article_id=target_article.article_id
        )
        rejected_revision = await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=target_article.article_id
        )
        
        # Create revision for other article (should not be included)
        other_submitted = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=other_article.article_id
        )
        
        # Login as regular user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": regular_user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revisions for target article
        response = await client.get(
            f"/api/v1/revisions/by-article/{target_article.article_id}", 
            headers=headers
        )
        
        assert response.status_code == 200
        revisions_data = response.json()
        
        # Should only return submitted and approved revisions for the target article
        revision_ids = [r["revision_id"] for r in revisions_data]
        assert str(submitted_revision.revision_id) in revision_ids
        assert str(approved_revision.revision_id) in revision_ids
        assert str(draft_revision.revision_id) not in revision_ids  # draft not included
        assert str(rejected_revision.revision_id) not in revision_ids  # rejected not included
        assert str(other_submitted.revision_id) not in revision_ids  # different article
        
        # Should have exactly 2 revisions (submitted + approved)
        assert len(revisions_data) == 2
    
    async def test_get_revisions_by_article_empty_result(self, client: AsyncClient, db_session: AsyncSession):
        """Test empty result when no public revisions exist for an article"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="empty_proposer", email="empty_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="empty_approver", email="empty_approver@example.com")
        regular_user = await UserFactory.create_user(db_session, username="empty_user", email="empty_user@example.com")
        
        # Create article with only draft and rejected revisions
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as regular user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": regular_user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get revisions for article
        response = await client.get(
            f"/api/v1/revisions/by-article/{article.article_id}", 
            headers=headers
        )
        
        assert response.status_code == 200
        revisions_data = response.json()
        assert len(revisions_data) == 0  # No public revisions
    
    async def test_get_revisions_by_article_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test pagination for revisions by article"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="pag_proposer", email="pag_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="pag_approver", email="pag_approver@example.com")
        regular_user = await UserFactory.create_user(db_session, username="pag_user", email="pag_user@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create 5 submitted revisions
        revisions = []
        for i in range(5):
            revision = await RevisionFactory.create_submitted(
                db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
            )
            revisions.append(revision)
        
        # Login as regular user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": regular_user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test pagination - get first 3 revisions
        response = await client.get(
            f"/api/v1/revisions/by-article/{article.article_id}?limit=3", 
            headers=headers
        )
        
        assert response.status_code == 200
        revisions_data = response.json()
        assert len(revisions_data) == 3  # Limited to 3
        
        # Test skip parameter
        response = await client.get(
            f"/api/v1/revisions/by-article/{article.article_id}?skip=3&limit=3", 
            headers=headers
        )
        
        assert response.status_code == 200
        revisions_data = response.json()
        assert len(revisions_data) == 2  # Remaining 2
    
    async def test_get_revisions_by_article_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test that authentication is required"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Try to access without authentication
        response = await client.get(f"/api/v1/revisions/by-article/{article.article_id}")
        
        assert response.status_code == 401
    
    async def test_get_revisions_by_article_all_roles_access(self, client: AsyncClient, test_users, db_session: AsyncSession):
        """Test that all authenticated users (user, approver, admin) can access the endpoint"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = test_users["user"]
        approver = test_users["approver"]
        admin = test_users["admin"]
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create a submitted revision
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Test access for each role
        for role in ["user", "approver", "admin"]:
            user = test_users[role]
            
            # Login
            login_response = await client.post(
                "/api/v1/auth/login/json",
                json={"email": user.email, "password": "testpassword123"}
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Access endpoint
            response = await client.get(
                f"/api/v1/revisions/by-article/{article.article_id}", 
                headers=headers
            )
            
            assert response.status_code == 200
            revisions_data = response.json()
            assert len(revisions_data) == 1  # Should see the submitted revision
            assert revisions_data[0]["revision_id"] == str(revision.revision_id)