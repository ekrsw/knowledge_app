"""Test pagination functionality for CRUDUser class.

This module contains tests for the pagination features implemented in Phase 3.1.
"""

import pytest
import asyncio
from unittest.mock import patch

from app.crud.user import user_crud
from app.schemas.user import UserCreate, PaginationParams
from app.models.user import GroupEnum


class TestCRUDUserPagination:
    """Test pagination functionality in CRUDUser."""

    @pytest.mark.asyncio
    async def test_get_all_users_without_pagination(self, clean_db_session):
        """Test get_all_users without pagination returns all users."""
        session = clean_db_session
        
        # Create test users
        users_to_create = []
        for i in range(5):
            user_in = UserCreate(
                username=f"testuser{i}",
                email=f"test{i}@example.com",
                password="testpass123",
                group=GroupEnum.CSC_1
            )
            users_to_create.append(user_in)
        
        # Create users
        created_users = []
        for user_in in users_to_create:
            user = await user_crud.create_user(session, user_in)
            created_users.append(user)
        
        # Test without pagination
        all_users = await user_crud.get_all_users(session)
        
        assert len(all_users) >= 5  # May include users from other tests
        created_usernames = {user.username for user in created_users}
        found_usernames = {user.username for user in all_users}
        assert created_usernames.issubset(found_usernames)

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, clean_db_session):
        """Test get_all_users with pagination limits results."""
        session = clean_db_session
        
        # Create test users
        users_to_create = []
        for i in range(10):
            user_in = UserCreate(
                username=f"pagtest{i}",
                email=f"pagtest{i}@example.com",
                password="testpass123",
                group=GroupEnum.CSC_1
            )
            users_to_create.append(user_in)
        
        # Create users
        for user_in in users_to_create:
            await user_crud.create_user(session, user_in)
        
        # Test with pagination - first page
        pagination = PaginationParams(page=1, limit=5)
        page1_users = await user_crud.get_all_users(session, pagination)
        
        assert len(page1_users) == 5
        
        # Test with pagination - second page
        pagination = PaginationParams(page=2, limit=5)
        page2_users = await user_crud.get_all_users(session, pagination)
        
        assert len(page2_users) >= 5  # May include users from other tests
        
        # Ensure different users on different pages
        page1_ids = {user.id for user in page1_users}
        page2_ids = {user.id for user in page2_users}
        assert page1_ids.isdisjoint(page2_ids)

    def test_pagination_params_validation(self):
        """Test PaginationParams validation."""
        
        # Valid pagination
        valid_pagination = PaginationParams(page=1, limit=20)
        assert valid_pagination.page == 1
        assert valid_pagination.limit == 20
        assert valid_pagination.offset == 0
        
        # Test offset calculation
        pagination = PaginationParams(page=3, limit=10)
        assert pagination.offset == 20
        
        # Test default values
        default_pagination = PaginationParams()
        assert default_pagination.page == 1
        assert default_pagination.limit == 20
        assert default_pagination.offset == 0
        
        # Test validation errors
        with pytest.raises(ValueError):
            PaginationParams(page=0)  # page must be >= 1
        
        with pytest.raises(ValueError):
            PaginationParams(limit=0)  # limit must be >= 1
        
        with pytest.raises(ValueError):
            PaginationParams(limit=101)  # limit must be <= 100

    @pytest.mark.asyncio
    async def test_get_users_paginated_full_response(self, clean_db_session):
        """Test get_users_paginated returns complete pagination info."""
        session = clean_db_session
        
        # Create test users
        users_to_create = []
        for i in range(25):
            user_in = UserCreate(
                username=f"paginatedtest{i}",
                email=f"paginatedtest{i}@example.com",
                password="testpass123",
                group=GroupEnum.CSC_1
            )
            users_to_create.append(user_in)
        
        # Create users
        for user_in in users_to_create:
            await user_crud.create_user(session, user_in)
        
        # Test first page
        pagination = PaginationParams(page=1, limit=10)
        result = await user_crud.get_users_paginated(session, pagination)
        
        assert result.page == 1
        assert result.limit == 10
        assert len(result.users) == 10
        assert result.total >= 25  # May include users from other tests
        assert result.pages >= 3  # At least 3 pages for 25+ users with limit 10
        assert result.has_next == True
        assert result.has_prev == False
        
        # Test middle page
        pagination = PaginationParams(page=2, limit=10)
        result = await user_crud.get_users_paginated(session, pagination)
        
        assert result.page == 2
        assert result.has_prev == True
        assert len(result.users) == 10
        
        # Test user dict structure
        if result.users:
            user_dict = result.users[0]
            expected_keys = {
                'id', 'username', 'email', 'full_name', 'ctstage_name', 
                'sweet_name', 'group', 'is_active', 'is_admin', 'is_sv',
                'created_at', 'updated_at'
            }
            assert set(user_dict.keys()) == expected_keys
            assert isinstance(user_dict['id'], str)
            assert isinstance(user_dict['is_active'], bool)

    @pytest.mark.asyncio
    async def test_get_users_paginated_edge_cases(self, clean_db_session):
        """Test pagination edge cases."""
        session = clean_db_session
        
        # Create few test users
        for i in range(3):
            user_in = UserCreate(
                username=f"edgetest{i}",
                email=f"edgetest{i}@example.com",
                password="testpass123",
                group=GroupEnum.CSC_1
            )
            await user_crud.create_user(session, user_in)
        
        # Test page beyond available data
        pagination = PaginationParams(page=100, limit=10)
        result = await user_crud.get_users_paginated(session, pagination)
        
        assert result.page == 100
        assert len(result.users) == 0
        assert result.has_next == False
        assert result.has_prev == True
        
        # Test with large limit
        pagination = PaginationParams(page=1, limit=100)
        result = await user_crud.get_users_paginated(session, pagination)
        
        assert result.page == 1
        assert result.limit == 100
        assert result.has_next == False
        assert result.pages <= 1

    @pytest.mark.asyncio
    async def test_pagination_backward_compatibility(self, clean_db_session):
        """Test that existing code still works (backward compatibility)."""
        session = clean_db_session
        
        # Create a test user
        user_in = UserCreate(
            username="compattest",
            email="compattest@example.com",
            password="testpass123",
            group=GroupEnum.CSC_1
        )
        created_user = await user_crud.create_user(session, user_in)
        
        # Test that get_all_users still works without pagination parameter
        all_users = await user_crud.get_all_users(session)
        
        assert isinstance(all_users, list)
        assert len(all_users) >= 1
        
        # Verify our created user is in the list
        found_user = None
        for user in all_users:
            if user.username == "compattest":
                found_user = user
                break
        
        assert found_user is not None
        assert found_user.id == created_user.id

    @pytest.mark.asyncio
    async def test_pagination_performance_logging(self, clean_db_session):
        """Test that pagination operations are properly logged."""
        session = clean_db_session
        
        # Create a test user
        user_in = UserCreate(
            username="logtest",
            email="logtest@example.com",
            password="testpass123",
            group=GroupEnum.CSC_1
        )
        await user_crud.create_user(session, user_in)
        
        # Test logging for paginated query
        with patch.object(user_crud.logger, 'debug') as mock_debug:
            pagination = PaginationParams(page=1, limit=5)
            await user_crud.get_users_paginated(session, pagination)
            
            # Check that debug logs were called
            assert mock_debug.call_count >= 2
            # Should have logs for getting paginated users and returning results
            call_args = [call.args[0] for call in mock_debug.call_args_list]
            assert any("Getting paginated users" in arg for arg in call_args)
            assert any("Returned paginated users" in arg for arg in call_args)

    @pytest.mark.asyncio
    async def test_pagination_with_empty_page(self, clean_db_session):
        """Test pagination behavior when requesting a page beyond available data."""
        session = clean_db_session
        
        # Request a page far beyond available data
        pagination = PaginationParams(page=1000, limit=10)
        result = await user_crud.get_users_paginated(session, pagination)
        
        assert result.page == 1000
        assert result.limit == 10
        assert result.total >= 0  # May have users from other tests
        assert result.has_next == False
        assert result.has_prev == True
        assert len(result.users) == 0  # This page should be empty

    def test_pagination_offset_calculation(self):
        """Test that offset calculation works correctly."""
        
        # Test various page/limit combinations
        test_cases = [
            (1, 10, 0),    # First page
            (2, 10, 10),   # Second page
            (3, 5, 10),    # Third page with limit 5
            (5, 20, 80),   # Fifth page with limit 20
        ]
        
        for page, limit, expected_offset in test_cases:
            pagination = PaginationParams(page=page, limit=limit)
            assert pagination.offset == expected_offset, f"Failed for page={page}, limit={limit}"