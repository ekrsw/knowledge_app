"""
Error Handling Integration Tests

Tests for comprehensive error handling including custom exceptions,
validation errors, status conflicts, and data integrity errors.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID

from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.revision_factory import RevisionFactory
from tests.factories.article_factory import ArticleFactory
from tests.factories.info_category_factory import InfoCategoryFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


class TestCustomExceptionHandling:
    """Test custom exception handling for highest priority endpoints"""
    
    async def test_approval_decision_proposal_not_found_error(self, client: AsyncClient, test_users):
        """Test ProposalNotFoundError handling in approval decision"""
        # Login as admin
        admin = test_users["admin"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": admin.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to process decision for non-existent revision
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
        
        # Should return 404 with proper error message
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
    
    async def test_approval_decision_approval_status_error(self, client: AsyncClient, db_session: AsyncSession):
        """Test ApprovalStatusError handling for invalid status"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="status_proposer", email="status_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="status_approver", email="status_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create revision in draft status (not submitted)
        draft_revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to approve draft revision (invalid status)
        decision_data = {
            "action": "approve",
            "comment": "Cannot approve draft",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{draft_revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        # Should return 400 with status error
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "status" in error_data["detail"].lower()
    
    async def test_approval_decision_approval_permission_error(self, client: AsyncClient, db_session: AsyncSession):
        """Test ApprovalPermissionError handling for unauthorized approver"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="perm_proposer", email="perm_proposer@example.com")
        designated_approver = await UserFactory.create_approver(db_session, approval_group, username="designated_approver", email="designated_approver@example.com")
        unauthorized_approver = await UserFactory.create_approver(db_session, approval_group, username="unauthorized_approver", email="unauthorized_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create submitted revision with designated approver
        revision = await RevisionFactory.create_submitted(
            db_session, 
            proposer=proposer, 
            approver=designated_approver,  # Only this approver should be allowed
            target_article_id=article.article_id
        )
        
        # Login as unauthorized approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "unauthorized_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to approve with wrong approver
        decision_data = {
            "action": "approve",
            "comment": "Unauthorized approval attempt",
            "priority": "medium"
        }
        
        response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=decision_data,
            headers=headers
        )
        
        # Should return 400 with permission error
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "designated approver" in error_data["detail"].lower()
    
    async def test_revision_create_article_not_found_error(self, client: AsyncClient, db_session: AsyncSession):
        """Test ArticleNotFoundError handling in revision creation"""
        # Create test users
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="article_proposer", email="article_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="article_approver", email="article_approver@example.com")
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "article_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to create revision for non-existent article
        revision_data = {
            "target_article_id": "non-existent-article-id",
            "approver_id": str(approver.id),
            "reason": "Test with non-existent article",
            "after_title": "Test Title",
            "after_info_category": str(info_category.category_id),
            "after_question": "Test question?",
            "after_answer": "Test answer"
        }
        
        response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
        
        # Should return 400 or 404 with article not found error
        assert response.status_code in [400, 404]
        error_data = response.json()
        assert "detail" in error_data
    
    async def test_revision_update_proposal_permission_error(self, client: AsyncClient, db_session: AsyncSession):
        """Test ProposalPermissionError handling for unauthorized update"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="update_proposer", email="update_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="update_approver", email="update_approver@example.com")
        other_user = await UserFactory.create_user(db_session, username="other_user", email="other_user@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as other user (not the proposer)
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "other_user@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update other user's revision
        update_data = {
            "reason": "Unauthorized update attempt",
            "after_title": "Hacked title"
        }
        
        response = await client.put(f"/api/v1/revisions/{revision.revision_id}", json=update_data, headers=headers)
        
        # Should return 403 with permission error
        assert response.status_code == 403
        error_data = response.json()
        assert "detail" in error_data
        assert "own" in error_data["detail"].lower() and "revisions" in error_data["detail"].lower()
    
    async def test_revision_update_proposal_status_error(self, client: AsyncClient, db_session: AsyncSession):
        """Test ProposalStatusError handling for invalid status update"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="status_update_proposer", email="status_update_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="status_update_approver", email="status_update_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Create submitted revision (cannot be updated by proposer)
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_update_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update submitted revision (should fail)
        update_data = {
            "reason": "Cannot update submitted revision",
            "after_title": "Should not update"
        }
        
        response = await client.put(f"/api/v1/revisions/{revision.revision_id}", json=update_data, headers=headers)
        
        # Should return 400 with status error
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert ("status" in error_data["detail"].lower() or 
                "cannot" in error_data["detail"].lower() or
                "not allowed" in error_data["detail"].lower())


class TestValidationErrorHandling:
    """Test validation error handling for complex business rules"""
    
    async def test_approval_decision_invalid_action_validation(self, client: AsyncClient, db_session: AsyncSession):
        """Test validation error for invalid approval action"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="val_proposer", email="val_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="val_approver", email="val_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "val_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Invalid action values
        invalid_actions = ["invalid_action", "APPROVE", "approve_now", "", None, 123, True]
        
        for invalid_action in invalid_actions:
            decision_data = {
                "action": invalid_action,
                "comment": "Test invalid action",
                "priority": "medium"
            }
            
            response = await client.post(
                f"/api/v1/approvals/{revision.revision_id}/decide",
                json=decision_data,
                headers=headers
            )
            
            # Should return 422 validation error
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data
    
    async def test_approval_decision_invalid_priority_validation(self, client: AsyncClient, db_session: AsyncSession):
        """Test validation error for invalid priority value"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="priority_proposer", email="priority_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="priority_approver", email="priority_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "priority_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Invalid priority values - test only real invalid ones that trigger validation
        invalid_priorities = ["invalid", "LOW", "super_urgent", "", 123, True]
        
        for i, invalid_priority in enumerate(invalid_priorities):
            # Create a new submitted revision for each test
            new_revision = await RevisionFactory.create_submitted(
                db_session, proposer=proposer, approver=approver, 
                target_article_id=article.article_id
            )
            
            decision_data = {
                "action": "approve",
                "comment": "Test invalid priority",
                "priority": invalid_priority
            }
            
            response = await client.post(
                f"/api/v1/approvals/{new_revision.revision_id}/decide",
                json=decision_data,
                headers=headers
            )
            
            # Should return 422 validation error
            assert response.status_code == 422, f"Expected 422 for priority {invalid_priority}, got {response.status_code}: {response.json()}"
            error_data = response.json()
            assert "detail" in error_data
    
    async def test_revision_create_missing_required_fields_validation(self, client: AsyncClient, test_users):
        """Test validation error for missing required fields in revision creation"""
        # Login as user
        user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test various combinations of missing required fields
        test_cases = [
            {},  # Empty request
            {"reason": "Missing everything else"},
            {"target_article_id": "test-article"},
            {"approver_id": str(uuid4())},
            {"after_title": "Title only"},
            {"target_article_id": "test", "reason": "Missing approver"},
            {"target_article_id": "test", "approver_id": str(uuid4())},  # Missing reason
        ]
        
        for incomplete_data in test_cases:
            response = await client.post("/api/v1/revisions/", json=incomplete_data, headers=headers)
            
            # Should return 422 validation error
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data
    
    async def test_revision_create_invalid_uuid_format_validation(self, client: AsyncClient, db_session: AsyncSession):
        """Test validation error for invalid UUID format in revision creation"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="uuid_proposer", email="uuid_proposer@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "uuid_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Invalid UUID formats
        invalid_uuids = [
            "not-a-uuid",
            "123",
            "12345678-1234-1234-1234",  # Incomplete
            "12345678-1234-1234-1234-12345678901z",  # Invalid character
            "",
            None
        ]
        
        for invalid_uuid in invalid_uuids:
            revision_data = {
                "target_article_id": article.article_id,
                "approver_id": invalid_uuid,
                "reason": "Test invalid UUID",
                "after_title": "Test Title",
                "after_info_category": str(info_category.category_id),
                "after_question": "Test question?",
                "after_answer": "Test answer"
            }
            
            response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
            
            # Should return 422 validation error
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data


class TestDataIntegrityErrorHandling:
    """Test data integrity error handling"""
    
    async def test_revision_create_nonexistent_approver_integrity(self, client: AsyncClient, db_session: AsyncSession):
        """Test data integrity error when creating revision with non-existent approver"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="integrity_proposer", email="integrity_proposer@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "integrity_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create revision with non-existent approver (valid UUID format but non-existent)
        fake_approver_id = str(uuid4())
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": fake_approver_id,
            "reason": "Test with fake approver",
            "after_title": "Test Title",
            "after_info_category": str(info_category.category_id),
            "after_question": "Test question?",
            "after_answer": "Test answer"
        }
        
        response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
        
        # Should return 400 or 404 with integrity error (not 201 success)
        assert response.status_code != 201, f"Expected error but got success: {response.json()}"
        assert response.status_code in [400, 404]
        error_data = response.json()
        assert "detail" in error_data
    
    async def test_revision_create_nonexistent_info_category_integrity(self, client: AsyncClient, db_session: AsyncSession):
        """Test data integrity error when creating revision with non-existent info category"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="category_proposer", email="category_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="category_approver", email="category_approver@example.com")
        article = await ArticleFactory.create_with_minimal_category(db_session, approval_group=approval_group)
        
        # Login as proposer
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "category_proposer@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create revision with non-existent info category
        fake_category_id = str(uuid4())
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": "Test with fake category",
            "after_title": "Test Title",
            "after_info_category": fake_category_id,  # Non-existent category
            "after_question": "Test question?",
            "after_answer": "Test answer"
        }
        
        response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
        
        # Should return 404 with integrity error (not 201 success)
        assert response.status_code != 201, f"Expected error but got success: {response.json()}"
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data


class TestConcurrencyErrorHandling:
    """Test concurrency and race condition error handling"""
    
    async def test_approval_decision_concurrent_processing(self, client: AsyncClient, db_session: AsyncSession):
        """Test handling of concurrent approval decisions on same revision"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="concurrent_proposer", email="concurrent_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="concurrent_approver", email="concurrent_approver@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_submitted(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Login as approver
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "concurrent_approver@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # First approval decision (approve)
        approve_data = {
            "action": "approve",
            "comment": "First approval",
            "priority": "medium"
        }
        
        first_response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=approve_data,
            headers=headers
        )
        
        # First request should succeed
        assert first_response.status_code == 200
        
        # Second approval decision (reject - should fail due to status change)
        reject_data = {
            "action": "reject",
            "comment": "Second decision attempt",
            "priority": "medium"
        }
        
        second_response = await client.post(
            f"/api/v1/approvals/{revision.revision_id}/decide",
            json=reject_data,
            headers=headers
        )
        
        # Second request should fail with status error
        assert second_response.status_code == 400
        error_data = second_response.json()
        assert "detail" in error_data
        assert "status" in error_data["detail"].lower()
    
    async def test_revision_update_after_status_change(self, client: AsyncClient, db_session: AsyncSession):
        """Test handling of revision update after status has changed"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        proposer = await UserFactory.create_user(db_session, username="status_change_proposer", email="status_change_proposer@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="status_change_approver", email="status_change_approver@example.com")
        admin = await UserFactory.create_admin(db_session, username="status_admin", email="status_admin@example.com")
        
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(
            db_session, proposer=proposer, approver=approver, target_article_id=article.article_id
        )
        
        # Admin changes status to submitted
        admin_login = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_admin@example.com", "password": "testpassword123"}
        )
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        status_change = await client.patch(
            f"/api/v1/revisions/{revision.revision_id}/status",
            json={"status": "submitted"},
            headers=admin_headers
        )
        assert status_change.status_code == 200
        
        # Now proposer tries to update (should fail due to status change)
        proposer_login = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "status_change_proposer@example.com", "password": "testpassword123"}
        )
        proposer_token = proposer_login.json()["access_token"]
        proposer_headers = {"Authorization": f"Bearer {proposer_token}"}
        
        update_data = {
            "reason": "Late update attempt",
            "after_title": "Should not update"
        }
        
        update_response = await client.put(
            f"/api/v1/revisions/{revision.revision_id}",
            json=update_data,
            headers=proposer_headers
        )
        
        # Should fail with status error (not 200 success)
        assert update_response.status_code != 200, f"Expected error but got success: {update_response.json()}"
        assert update_response.status_code == 400
        error_data = update_response.json()
        assert "detail" in error_data
        assert ("status" in error_data["detail"].lower() or 
                "cannot" in error_data["detail"].lower() or
                "not allowed" in error_data["detail"].lower())


class TestSystemErrorHandling:
    """Test system-level error handling"""
    
    async def test_malformed_json_request_handling(self, client: AsyncClient, test_users):
        """Test handling of malformed JSON requests"""
        # Login as user
        user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Send malformed JSON
        import httpx
        request = httpx.Request(
            method="POST",
            url=f"{client.base_url}/api/v1/revisions/",
            headers=headers,
            content='{"invalid": json, "malformed": }'  # Invalid JSON
        )
        
        response = await client.send(request)
        
        # Should return 422 with JSON parse error
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    async def test_invalid_content_type_handling(self, client: AsyncClient, test_users):
        """Test handling of invalid content type"""
        # Login as user
        user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": user.email, "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain"  # Wrong content type
        }
        
        # Send data with wrong content type
        response = await client.post(
            "/api/v1/revisions/",
            headers=headers,
            content="This is not JSON"
        )
        
        # Should return 422 or 415
        assert response.status_code in [415, 422]
        error_data = response.json()
        assert "detail" in error_data
    
    async def test_extremely_large_request_handling(self, client: AsyncClient, db_session: AsyncSession):
        """Test handling of extremely large requests"""
        # Create test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        info_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        user = await UserFactory.create_user(db_session, username="large_user", email="large_user@example.com")
        approver = await UserFactory.create_approver(db_session, approval_group, username="large_approver", email="large_approver@example.com")
        article = await ArticleFactory.create(db_session, info_category=info_category, approval_group=approval_group)
        
        # Login as user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "large_user@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create extremely large request data
        huge_string = "A" * (1024 * 1024)  # 1MB string
        
        revision_data = {
            "target_article_id": article.article_id,
            "approver_id": str(approver.id),
            "reason": huge_string,  # Extremely large reason
            "after_title": huge_string,
            "after_question": huge_string,
            "after_answer": huge_string
        }
        
        response = await client.post("/api/v1/revisions/", json=revision_data, headers=headers)
        
        # Should either succeed with truncation or fail with size error
        assert response.status_code in [201, 400, 413, 422]
        if response.status_code != 201:
            error_data = response.json()
            assert "detail" in error_data