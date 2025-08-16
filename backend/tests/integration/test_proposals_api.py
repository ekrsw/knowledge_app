"""
Tests for proposal API endpoints
"""
import pytest
from typing import Dict, Any
from uuid import UUID
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

from app.models.user import User
from app.models.revision import Revision
from tests.factories.user_factory import UserFactory
from tests.factories.revision_factory import RevisionFactory
from tests.factories.article_factory import ArticleFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.utils.auth import get_auth_token


class TestProposalsMyProposals:
    """Test /proposals/my-proposals endpoint"""
    
    async def test_get_my_proposals_success(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession
    ):
        """Test successful retrieval of user's proposals"""
        # Create test user
        user = await UserFactory.create(db_session, role="user")
        
        # Create test article
        article = await ArticleFactory.create(db_session)
        
        # Create proposals for the user
        proposal1 = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="draft"
        )
        proposal2 = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="submitted"
        )
        
        # Create proposal for different user (should not be returned)
        other_user = await UserFactory.create(db_session, role="user")
        await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=other_user,
            status="draft"
        )
        
        # Get auth token
        token = await get_auth_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request
        response = await client.get(
            "/api/v1/proposals/my-proposals",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify returned proposals belong to the user
        proposal_ids = {p["revision_id"] for p in data}
        assert str(proposal1.revision_id) in proposal_ids
        assert str(proposal2.revision_id) in proposal_ids
    
    async def test_get_my_proposals_with_null_approver(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test retrieval of proposals with NULL approver_id"""
        # Create test user
        user = await UserFactory.create(db_session, role="user")
        
        # Create test article
        article = await ArticleFactory.create(db_session)
        
        # Create proposal with NULL approver_id (simulating legacy data)
        proposal = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            approver=None,  # NULL approver
            status="draft"
        )
        
        # Get auth token
        token = await get_auth_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request
        response = await client.get(
            "/api/v1/proposals/my-proposals",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert len(data) == 1
        
        # Verify the proposal with NULL approver_id is returned correctly
        assert data[0]["revision_id"] == str(proposal.revision_id)
        assert data[0]["approver_id"] is None  # Should be None, not cause validation error
        assert data[0]["status"] == "draft"
    
    async def test_get_my_proposals_with_status_filter(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test filtering proposals by status"""
        # Create test user
        user = await UserFactory.create(db_session, role="user")
        
        # Create test article
        article = await ArticleFactory.create(db_session)
        
        # Create proposals with different statuses
        draft_proposal = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="draft"
        )
        submitted_proposal = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="submitted"
        )
        approved_proposal = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="approved"
        )
        
        # Get auth token
        token = await get_auth_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test filter for draft status
        response = await client.get(
            "/api/v1/proposals/my-proposals?status=draft",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["revision_id"] == str(draft_proposal.revision_id)
        
        # Test filter for submitted status
        response = await client.get(
            "/api/v1/proposals/my-proposals?status=submitted",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["revision_id"] == str(submitted_proposal.revision_id)
    
    async def test_get_my_proposals_empty(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test when user has no proposals"""
        # Create test user
        user = await UserFactory.create(db_session, role="user")
        
        # Get auth token
        token = await get_auth_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request
        response = await client.get(
            "/api/v1/proposals/my-proposals",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    async def test_get_my_proposals_unauthorized(
        self,
        client: AsyncClient
    ):
        """Test access without authentication"""
        response = await client.get("/api/v1/proposals/my-proposals")
        assert response.status_code == 401


class TestProposalsForApproval:
    """Test /proposals/for-approval endpoint"""
    
    async def test_get_proposals_for_approval_as_approver(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test getting proposals that need approval"""
        # Create approval group
        approval_group = await ApprovalGroupFactory.create(db_session)
        
        # Create approver user
        approver = await UserFactory.create(
            db_session, 
            role="approver",
            approval_group=approval_group
        )
        
        # Create test article assigned to the approval group
        article = await ArticleFactory.create(db_session, approval_group=approval_group)
        
        # Create proposal assigned to this approver
        proposal_for_approver = await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            approver=approver,
            status="submitted"
        )
        
        # Create proposal assigned to different approver with different approval group
        other_approval_group = await ApprovalGroupFactory.create(db_session)
        other_approver = await UserFactory.create(
            db_session, 
            role="approver",
            approval_group=other_approval_group
        )
        other_article = await ArticleFactory.create(db_session, approval_group=other_approval_group)
        await RevisionFactory.create(
            db_session,
            target_article_id=other_article.article_id,
            approver=other_approver,
            status="submitted"
        )
        
        # Get auth token
        token = await get_auth_token(approver)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request
        response = await client.get(
            "/api/v1/proposals/for-approval",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["revision_id"] == str(proposal_for_approver.revision_id)
    
    async def test_get_proposals_for_approval_as_regular_user(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test that regular users cannot access approval queue"""
        # Create regular user
        user = await UserFactory.create(db_session, role="user")
        
        # Get auth token
        token = await get_auth_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request
        response = await client.get(
            "/api/v1/proposals/for-approval",
            headers=headers
        )
        
        # Should be forbidden for regular users
        assert response.status_code == 403


class TestProposalStatistics:
    """Test /proposals/statistics endpoint"""
    
    async def test_get_proposal_statistics_own(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test getting own proposal statistics"""
        # Create test user
        user = await UserFactory.create(db_session, role="user")
        
        # Create test article
        article = await ArticleFactory.create(db_session)
        
        # Create proposals with different statuses
        await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="draft"
        )
        await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="submitted"
        )
        await RevisionFactory.create(
            db_session,
            target_article_id=article.article_id,
            proposer=user,
            status="approved"
        )
        
        # Get auth token
        token = await get_auth_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request
        response = await client.get(
            "/api/v1/proposals/statistics",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "draft" in data
        assert "submitted" in data  
        assert "approved" in data
        assert data["total"] == 3
        assert data["draft"] == 1
        assert data["submitted"] == 1
        assert data["approved"] == 1