"""
Test for rejected revision permissions
Tests that both proposer and approver can view rejected revisions
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.revision_factory import RevisionFactory
from tests.factories.article_factory import ArticleFactory
from tests.factories.info_category_factory import InfoCategoryFactory
from app.repositories.revision import revision_repository
from tests.utils.auth import create_auth_headers


pytestmark = pytest.mark.asyncio


class TestRejectedRevisionPermissions:
    """Test rejected revision access permissions"""
    
    async def test_proposer_can_see_own_rejected_revision(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that proposer can see their own rejected revision"""
        # Setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        proposer = await UserFactory.create_user(db_session, username="proposer", email="proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver", email="approver@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create rejected revision
        revision = await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as proposer
        headers = await create_auth_headers(proposer)
        
        # Get revision
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["revision_id"] == str(revision.revision_id)
        assert response.json()["status"] == "rejected"
        
        # Get revisions list should include rejected
        response = await client.get("/api/v1/revisions/", headers=headers)
        assert response.status_code == 200
        revision_ids = [r["revision_id"] for r in response.json()]
        assert str(revision.revision_id) in revision_ids
    
    async def test_approver_can_see_rejected_revision_they_processed(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that approver can see rejected revisions they were assigned to"""
        # Setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        proposer = await UserFactory.create_user(db_session, username="proposer2", email="proposer2@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver2", email="approver2@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create rejected revision
        revision = await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as approver
        headers = await create_auth_headers(approver)
        
        # Get revision - approver should be able to see it
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["revision_id"] == str(revision.revision_id)
        assert response.json()["status"] == "rejected"
        assert response.json()["approver_id"] == str(approver.id)
        
        # Get revisions list should include rejected
        response = await client.get("/api/v1/revisions/", headers=headers)
        assert response.status_code == 200
        revision_ids = [r["revision_id"] for r in response.json()]
        assert str(revision.revision_id) in revision_ids
    
    async def test_other_user_cannot_see_rejected_revision(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that other users cannot see rejected revisions they're not involved with"""
        # Setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        proposer = await UserFactory.create_user(db_session, username="proposer3", email="proposer3@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver3", email="approver3@example.com")
        other_user = await UserFactory.create_user(db_session, username="other_user", email="other@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create rejected revision
        revision = await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as other user
        headers = await create_auth_headers(other_user)
        
        # Get revision - should be forbidden
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        assert response.status_code == 403
        
        # Get revisions list should NOT include rejected
        response = await client.get("/api/v1/revisions/", headers=headers)
        assert response.status_code == 200
        revision_ids = [r["revision_id"] for r in response.json()]
        assert str(revision.revision_id) not in revision_ids
    
    async def test_admin_can_see_all_rejected_revisions(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that admin can see all rejected revisions"""
        # Setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        proposer = await UserFactory.create_user(db_session, username="proposer4", email="proposer4@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver4", email="approver4@example.com")
        admin = await UserFactory.create_admin(db_session, username="admin_rejected", email="admin_rejected@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create rejected revision
        revision = await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as admin
        headers = await create_auth_headers(admin)
        
        # Get revision - admin should be able to see it
        response = await client.get(f"/api/v1/revisions/{revision.revision_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["revision_id"] == str(revision.revision_id)
        assert response.json()["status"] == "rejected"
        
        # Get revisions list should include rejected
        response = await client.get("/api/v1/revisions/", headers=headers)
        assert response.status_code == 200
        revision_ids = [r["revision_id"] for r in response.json()]
        assert str(revision.revision_id) in revision_ids
    
    async def test_get_mixed_access_revisions_with_approver(
        self, db_session: AsyncSession
    ):
        """Test repository method get_mixed_access_revisions includes rejected for approver"""
        # Setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        proposer = await UserFactory.create_user(db_session, username="proposer5", email="proposer5@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver5", email="approver5@example.com")
        other_user = await UserFactory.create_user(db_session, username="other5", email="other5@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create rejected revision with approver
        rejected_revision = await RevisionFactory.create_rejected(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Create another rejected revision with different approver (should not be visible)
        other_approver = await UserFactory.create_approver(db_session, approval_group, username="other_approver", email="other_approver@example.com")
        other_rejected = await RevisionFactory.create_rejected(
            db_session, proposer=other_user, approver=other_approver, target_article_id=article.article_id
        )
        
        # Test repository method as approver
        revisions = await revision_repository.get_mixed_access_revisions(
            db_session, user_id=approver.id
        )
        revision_ids = [str(r.revision_id) for r in revisions]
        
        # Approver should see the rejected revision they were assigned to
        assert str(rejected_revision.revision_id) in revision_ids
        # But not the one assigned to another approver
        assert str(other_rejected.revision_id) not in revision_ids
    
    async def test_get_revisions_by_status_rejected_with_approver(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test GET /api/v1/revisions/by-status/rejected endpoint with approver"""
        # Setup
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        proposer1 = await UserFactory.create_user(db_session, username="proposer6", email="proposer6@example.com")
        proposer2 = await UserFactory.create_user(db_session, username="proposer7", email="proposer7@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="approver6", email="approver6@example.com")
        other_approver = await UserFactory.create_approver(db_session, approval_group, username="other_approver2", email="other_approver2@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create rejected revisions
        rejected1 = await RevisionFactory.create_rejected(
            db_session, proposer=proposer1, approver=approver, target_article_id=article.article_id
        )
        rejected2 = await RevisionFactory.create_rejected(
            db_session, proposer=proposer2, approver=other_approver, target_article_id=article.article_id
        )
        
        # Login as approver
        headers = await create_auth_headers(approver)
        
        # Get rejected revisions
        response = await client.get("/api/v1/revisions/by-status/rejected", headers=headers)
        assert response.status_code == 200
        
        revision_ids = [r["revision_id"] for r in response.json()]
        # Should see the one they were assigned to
        assert str(rejected1.revision_id) in revision_ids
        # Should NOT see the one assigned to another approver
        assert str(rejected2.revision_id) not in revision_ids