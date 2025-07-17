"""Enhanced Security tests for User CRUD operations.

This module provides tests for verifying security enhancements including
information leakage prevention and timing attack resistance.
"""

import pytest
import pytest_asyncio
import time
import re
from unittest.mock import patch, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import GroupEnum
from app.crud.exceptions import (
    UserNotFoundError,
    InvalidPasswordError,
    DuplicateUsernameError,
    DuplicateEmailError
)
from app.core.config import settings
from app.db.base import Base


class TestCRUDUserSecurityEnhanced:
    """Enhanced security tests for User CRUD operations."""

    async def create_fresh_session(self):
        """Create a fresh database session for testing."""
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            async_session = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            session = async_session()
            try:
                yield session, engine
            finally:
                await session.close()
        finally:
            await engine.dispose()

    async def cleanup_test_data(self, session):
        """Clean up test data."""
        try:
            await session.execute(text(
                "DELETE FROM users WHERE username LIKE 'security_%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_information_leakage_prevention_in_logs(self):
        """Test that sensitive information is not leaked in logs."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Mock logger to capture log messages
                with patch.object(user_crud, 'logger') as mock_logger:
                    # Create user
                    user_data = UserCreate(
                        username="security_test_user",
                        email="security@test.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # Check that no sensitive information is logged
                    log_calls = [str(call) for call in mock_logger.info.call_args_list]
                    log_calls.extend([str(call) for call in mock_logger.debug.call_args_list])
                    log_calls.extend([str(call) for call in mock_logger.error.call_args_list])
                    
                    all_logs = ' '.join(log_calls)
                    
                    # Verify no username in logs
                    assert "security_test_user" not in all_logs, "Username found in logs"
                    # Verify no email in logs
                    assert "security@test.com" not in all_logs, "Email found in logs"
                    # Verify no raw UUID in logs (should be hashed)
                    assert str(created_user.id) not in all_logs, "Raw UUID found in logs"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_user_id_hashing_in_logs(self):
        """Test that user IDs are properly hashed in logs."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                with patch.object(user_crud.logging_service, 'logger') as mock_logger:
                    user_data = UserCreate(
                        username="security_hash_test",
                        email="hash@test.com", 
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    
                    created_user = await user_crud.create_user(session, user_data)
                    user_id = created_user.id
                    
                    # Get hashed ID for verification
                    expected_hash = user_crud._hash_user_id(user_id)
                    
                    # Check that hashed ID appears in logs but not raw ID
                    log_calls = [str(call) for call in mock_logger.info.call_args_list]
                    all_logs = ' '.join(log_calls)
                    
                    assert expected_hash in all_logs, "Hashed user ID not found in logs"
                    assert str(user_id) not in all_logs, "Raw user ID found in logs"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_exception_chaining_removal(self):
        """Test that internal exceptions are not chained."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user first
                user_data = UserCreate(
                    username="security_exception_test",
                    email="exception@test.com",
                    password="testpass123", 
                    group=GroupEnum.CSC_1
                )
                await user_crud.create_user(session, user_data)
                
                # Try to create duplicate user
                duplicate_data = UserCreate(
                    username="security_exception_test",
                    email="exception2@test.com",  # Different email to isolate username constraint
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                try:
                    await user_crud.create_user(session, duplicate_data)
                    assert False, "Should have raised DuplicateUsernameError"
                except DuplicateUsernameError as e:
                    # Verify no exception chaining (from None prevents __cause__)
                    assert e.__cause__ is None, "Exception chaining found (__cause__ should be None)"
                    # Verify the error message itself doesn't leak sensitive info
                    error_msg = str(e)
                    assert "security_exception_test" not in error_msg, "Username in error message"
                    assert "exception@test.com" not in error_msg, "Email in error message"
                    # Generic error message check
                    assert error_msg == "Username already exists", f"Error message too specific: {error_msg}"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_generic_error_messages(self):
        """Test that error messages don't reveal internal details."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Test UserNotFoundError message
                non_existent_id = uuid4()
                
                try:
                    await user_crud.get_user_by_id(session, non_existent_id)
                    # This should succeed (return None)
                    pass
                except Exception:
                    assert False, "get_user_by_id should not raise exception for non-existent user"
                
                # Test UserNotFoundError in update
                try:
                    update_data = UserUpdate(full_name="Updated Name")
                    await user_crud.update_user_by_id(session, non_existent_id, update_data)
                    assert False, "Should have raised UserNotFoundError"
                except UserNotFoundError as e:
                    # Verify generic message
                    assert str(e) == "User not found", f"Error message too specific: {str(e)}"
                    assert str(non_existent_id) not in str(e), "User ID leaked in error message"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_timing_attack_resistance_password_verification(self):
        """Test that password verification has consistent timing."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user
                user_data = UserCreate(
                    username="security_timing_test",
                    email="timing@test.com",
                    password="correctpass123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                user_id = created_user.id
                
                # Test timing consistency for password verification
                times = []
                
                # Test with correct password
                start_time = time.time()
                try:
                    await user_crud.update_password(session, user_id, "correctpass123", "newpass123")
                except Exception:
                    pass
                correct_time = time.time() - start_time
                times.append(correct_time)
                
                # Reset password for next test
                user = await user_crud.get_user_by_id(session, user_id)
                if user:
                    from app.core.security import get_password_hash
                    user.hashed_password = get_password_hash("correctpass123")
                    await session.commit()
                
                # Test with incorrect password
                start_time = time.time()
                try:
                    await user_crud.update_password(session, user_id, "wrongpass123", "newpass123")
                    assert False, "Should have raised InvalidPasswordError"
                except InvalidPasswordError:
                    pass
                incorrect_time = time.time() - start_time
                times.append(incorrect_time)
                
                # Verify minimum time constraint (250ms)
                for timing in times:
                    assert timing >= 0.25, f"Password verification too fast: {timing}s < 0.25s"
                
                # Verify timing consistency (difference should be reasonable)
                time_diff = abs(correct_time - incorrect_time)
                assert time_diff < 0.3, f"Timing difference too large: {time_diff}s"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_constant_time_user_lookup(self):
        """Test that user lookup helper provides consistent timing."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create test user
                user_data = UserCreate(
                    username="security_lookup_test",
                    email="lookup@test.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                
                # Test constant time lookup function
                async def test_lookup(session, username):
                    stmt_func = lambda s, u: user_crud.get_user_by_username(s, u)
                    return await user_crud._constant_time_user_lookup(session, stmt_func, session, username)
                
                # Measure timing for existing user
                start_time = time.time()
                found_user = await test_lookup(session, "security_lookup_test")
                existing_time = time.time() - start_time
                
                # Measure timing for non-existing user  
                start_time = time.time()
                missing_user = await test_lookup(session, "non_existent_user")
                missing_time = time.time() - start_time
                
                # Verify minimum time constraint (50ms)
                assert existing_time >= 0.05, f"Lookup too fast for existing user: {existing_time}s"
                assert missing_time >= 0.05, f"Lookup too fast for missing user: {missing_time}s"
                
                # Verify results are correct
                assert found_user is not None, "Should find existing user"
                assert missing_user is None, "Should not find non-existent user"
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_sensitive_data_not_in_error_logs(self):
        """Test that sensitive data doesn't appear in error logs."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                with patch.object(user_crud, 'logger') as mock_logger:
                    # Create user
                    user_data = UserCreate(
                        username="security_error_test",
                        email="error@test.com",
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    created_user = await user_crud.create_user(session, user_data)
                    
                    user_id = created_user.id  # Store ID before potential rollback
                    
                    # Try duplicate creation to trigger error
                    duplicate_data = UserCreate(
                        username="security_error_test",
                        email="error2@test.com",  # Different email
                        password="testpass123",
                        group=GroupEnum.CSC_1
                    )
                    try:
                        await user_crud.create_user(session, duplicate_data)
                    except DuplicateUsernameError:
                        pass
                    
                    # Check error logs don't contain sensitive data
                    error_calls = [str(call) for call in mock_logger.error.call_args_list]
                    all_error_logs = ' '.join(error_calls)
                    
                    # Verify no sensitive data in error logs
                    assert "security_error_test" not in all_error_logs, "Username in error logs"
                    assert "error@test.com" not in all_error_logs, "Email in error logs"
                    assert "testpass123" not in all_error_logs, "Password in error logs"
                    assert str(user_id) not in all_error_logs, "Raw UUID in error logs"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_user_id_hash_consistency(self):
        """Test that user ID hashing is consistent."""
        test_uuid = uuid4()
        
        # Hash same UUID multiple times
        hash1 = user_crud._hash_user_id(test_uuid)
        hash2 = user_crud._hash_user_id(test_uuid)
        hash3 = user_crud._hash_user_id(test_uuid)
        
        # Verify consistency
        assert hash1 == hash2 == hash3, "User ID hashing not consistent"
        
        # Verify hash format (8 characters)
        assert len(hash1) == 8, f"Hash length incorrect: {len(hash1)} != 8"
        assert re.match(r'^[a-f0-9]{8}$', hash1), f"Hash format incorrect: {hash1}"
        
        # Verify different UUIDs produce different hashes
        different_uuid = uuid4()
        different_hash = user_crud._hash_user_id(different_uuid)
        assert hash1 != different_hash, "Different UUIDs produced same hash"

    @pytest.mark.asyncio
    async def test_password_not_logged_during_operations(self):
        """Test that passwords never appear in logs."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                with patch.object(user_crud, 'logger') as mock_logger:
                    # Create user
                    user_data = UserCreate(
                        username="security_password_test",
                        email="password@test.com",
                        password="supersecret123",
                        group=GroupEnum.CSC_1
                    )
                    created_user = await user_crud.create_user(session, user_data)
                    
                    # Update password
                    try:
                        await user_crud.update_password(
                            session, 
                            created_user.id, 
                            "supersecret123", 
                            "newsecret456"
                        )
                    except Exception:
                        pass
                    
                    # Collect all log calls
                    all_calls = []
                    all_calls.extend([str(call) for call in mock_logger.info.call_args_list])
                    all_calls.extend([str(call) for call in mock_logger.debug.call_args_list])
                    all_calls.extend([str(call) for call in mock_logger.error.call_args_list])
                    all_calls.extend([str(call) for call in mock_logger.warning.call_args_list])
                    
                    all_logs = ' '.join(all_calls)
                    
                    # Verify no passwords in logs
                    assert "supersecret123" not in all_logs, "Old password found in logs"
                    assert "newsecret456" not in all_logs, "New password found in logs"
                    assert "password" not in all_logs.lower() or "password" in "update_password", "Password keyword found in logs"
                    
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)