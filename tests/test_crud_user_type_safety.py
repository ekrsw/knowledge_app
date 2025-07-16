"""User CRUD operations type safety tests.

This module provides tests for ensuring type safety in User CRUD operations,
specifically focusing on UUID type handling.
"""

import pytest
import pytest_asyncio
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import GroupEnum
from app.crud.exceptions import (
    UserNotFoundError,
    DuplicateUsernameError,
    DuplicateEmailError,
    InvalidPasswordError,
    MissingRequiredFieldError,
    DatabaseIntegrityError
)
from app.core.config import settings
from app.db.base import Base


class TestCRUDUserTypeSafety:
    """User CRUD operations type safety tests."""

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
                "DELETE FROM users WHERE username LIKE 'uuid_%'"
            ))
            await session.commit()
        except Exception:
            await session.rollback()

    @pytest.mark.asyncio
    async def test_get_user_by_id_uuid_type(self):
        """Test get_user_by_id with UUID type parameter."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user
                user_data = UserCreate(
                    username="uuid_test_user",
                    email="uuid_test@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                user_uuid = created_user.id
                await session.commit()
                
                # Test with UUID object (should work)
                retrieved_user = await user_crud.get_user_by_id(session, user_uuid)
                assert retrieved_user is not None
                assert retrieved_user.id == user_uuid
                assert retrieved_user.username == "uuid_test_user"
                
                # Test with non-existent UUID (should return None)
                non_existent_uuid = uuid4()
                non_existent_user = await user_crud.get_user_by_id(session, non_existent_uuid)
                assert non_existent_user is None
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_user_by_id_uuid_type(self):
        """Test update_user_by_id with UUID type parameter."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user
                user_data = UserCreate(
                    username="uuid_update_user",
                    email="uuid_update@example.com", 
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                user_uuid = created_user.id
                await session.commit()
                
                # Update user with UUID object
                update_data = UserUpdate(
                    full_name="Updated Name",
                    group=GroupEnum.CSC_2
                )
                updated_user = await user_crud.update_user_by_id(session, user_uuid, update_data)
                assert updated_user.id == user_uuid
                assert updated_user.full_name == "Updated Name"
                assert updated_user.group == GroupEnum.CSC_2
                
                # Test with non-existent UUID (should raise UserNotFoundError)
                non_existent_uuid = uuid4()
                with pytest.raises(UserNotFoundError):
                    await user_crud.update_user_by_id(session, non_existent_uuid, update_data)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_update_password_uuid_type(self):
        """Test update_password with UUID type parameter."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user
                user_data = UserCreate(
                    username="uuid_password_user",
                    email="uuid_password@example.com",
                    password="oldpassword123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                user_uuid = created_user.id
                await session.commit()
                
                # Update password with UUID object
                updated_user = await user_crud.update_password(
                    session, 
                    user_uuid, 
                    "oldpassword123", 
                    "newpassword123"
                )
                assert updated_user.id == user_uuid
                
                # Test with non-existent UUID (should raise UserNotFoundError)
                non_existent_uuid = uuid4()
                with pytest.raises(UserNotFoundError):
                    await user_crud.update_password(
                        session, 
                        non_existent_uuid, 
                        "oldpassword123", 
                        "newpassword123"
                    )
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_delete_user_uuid_type(self):
        """Test delete_user with UUID type parameter."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user
                user_data = UserCreate(
                    username="uuid_delete_user",
                    email="uuid_delete@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                user_uuid = created_user.id
                await session.commit()
                
                # Delete user with UUID object
                deleted_user = await user_crud.delete_user_by_id(session, user_uuid)
                assert deleted_user.id == user_uuid
                
                # Verify user is deleted
                retrieved_user = await user_crud.get_user_by_id(session, user_uuid)
                assert retrieved_user is None
                
                # Test with non-existent UUID (should raise UserNotFoundError)
                non_existent_uuid = uuid4()
                with pytest.raises(UserNotFoundError):
                    await user_crud.delete_user_by_id(session, non_existent_uuid)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)

    @pytest.mark.asyncio
    async def test_uuid_consistency_across_operations(self):
        """Test UUID consistency across different CRUD operations."""
        async for session, engine in self.create_fresh_session():
            try:
                await self.cleanup_test_data(session)
                
                # Create user
                user_data = UserCreate(
                    username="uuid_consistency_user",
                    email="uuid_consistency@example.com",
                    password="testpass123",
                    group=GroupEnum.CSC_1
                )
                created_user = await user_crud.create_user(session, user_data)
                user_uuid = created_user.id
                await session.commit()
                
                # Verify UUID is consistent across operations
                assert isinstance(user_uuid, UUID)
                
                # Get user by ID
                retrieved_user = await user_crud.get_user_by_id(session, user_uuid)
                assert retrieved_user is not None
                assert retrieved_user.id == user_uuid
                assert isinstance(retrieved_user.id, UUID)
                
                # Update user
                update_data = UserUpdate(full_name="Consistent Name")
                updated_user = await user_crud.update_user_by_id(session, user_uuid, update_data)
                assert updated_user.id == user_uuid
                assert isinstance(updated_user.id, UUID)
                
                # Update password
                password_updated_user = await user_crud.update_password(
                    session, 
                    user_uuid, 
                    "testpass123", 
                    "newpass123"
                )
                assert password_updated_user.id == user_uuid
                assert isinstance(password_updated_user.id, UUID)
                
                # Delete user
                deleted_user = await user_crud.delete_user_by_id(session, user_uuid)
                assert deleted_user.id == user_uuid
                assert isinstance(deleted_user.id, UUID)
                
            except Exception:
                await session.rollback()
                raise
            finally:
                await self.cleanup_test_data(session)