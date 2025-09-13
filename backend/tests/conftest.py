"""
Test configuration and shared fixtures
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

# FakeRedis for mocking Redis
try:
    import fakeredis.aioredis as fakeredis
except ImportError:
    fakeredis = None

from app.core.config import settings
from app.api.dependencies import get_db
from app.models import Base
from app.models.user import User
from app.models.approval_group import ApprovalGroup

# Import test factories
from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory


# Test database URL (using in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_maker(test_engine):
    """Create test session maker"""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


@pytest_asyncio.fixture
async def db_session(test_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for each test"""
    async with test_session_maker() as session:
        try:
            yield session
        finally:
            # Clean up all test data after each test to prevent leakage
            from app.models.notification import SimpleNotification
            from app.models.revision import Revision
            from app.models.article import Article
            from app.models.user import User
            from app.models.info_category import InfoCategory
            from app.models.approval_group import ApprovalGroup
            
            await session.rollback()
            
            # Delete in correct order to avoid foreign key constraints
            for model in [SimpleNotification, Revision, Article, User, InfoCategory, ApprovalGroup]:
                await session.execute(text(f"DELETE FROM {model.__tablename__}"))
            
            await session.commit()


@pytest_asyncio.fixture
async def fake_redis():
    """Create fake Redis for testing"""
    if fakeredis is None:
        pytest.skip("fakeredis not installed")
    
    redis = fakeredis.FakeRedis()
    yield redis
    await redis.aclose()


@pytest_asyncio.fixture
async def client(test_engine, db_session: AsyncSession, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP client for API testing"""
    
    # Import app modules individually to avoid importing the pre-configured app
    from fastapi import FastAPI
    from app.api.v1.api import api_router
    from app.core.config import settings
    from httpx import ASGITransport
    
    # Create a new FastAPI app instance for testing
    test_app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Include the API router
    test_app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Override the database dependency for this test app
    async def override_get_db():
        yield db_session
    
    # Override the database dependency function
    test_app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac
    
    # Clean up after test
    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_approval_groups(db_session: AsyncSession) -> Dict[str, ApprovalGroup]:
    """Create test approval groups for all tests"""
    # Create different types of approval groups
    dev_group = await ApprovalGroupFactory.create_development_group(db_session)
    qa_group = await ApprovalGroupFactory.create_quality_group(db_session)
    mgmt_group = await ApprovalGroupFactory.create_management_group(db_session)
    
    return {
        "development": dev_group,
        "quality": qa_group,
        "management": mgmt_group
    }


@pytest_asyncio.fixture
async def test_users(
    db_session: AsyncSession, 
    test_approval_groups: Dict[str, ApprovalGroup]
) -> Dict[str, User]:
    """Create test users with different roles for all tests"""
    
    # Create admin user
    admin_user = await UserFactory.create_admin(
        db_session,
        username="testadmin",
        email="admin@test.com",
        full_name="Test Admin User"
    )
    
    # Create approver user with development group
    approver_user = await UserFactory.create_approver(
        db_session,
        approval_group=test_approval_groups["development"],
        username="testapprover",
        email="approver@test.com",
        full_name="Test Approver User"
    )
    
    # Create approver user with quality group
    qa_approver = await UserFactory.create_approver(
        db_session,
        approval_group=test_approval_groups["quality"],
        username="qaapprover",
        email="qaapprover@test.com",
        full_name="QA Approver User"
    )
    
    # Create regular user
    regular_user = await UserFactory.create_user(
        db_session,
        username="testuser",
        email="user@test.com",
        full_name="Test Regular User"
    )
    
    # Create inactive user for testing
    inactive_user = await UserFactory.create_user(
        db_session,
        username="inactiveuser",
        email="inactive@test.com",
        full_name="Inactive Test User",
        is_active=False
    )
    
    return {
        "admin": admin_user,
        "approver": approver_user,
        "qa_approver": qa_approver,
        "user": regular_user,
        "inactive": inactive_user
    }


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient, 
    test_users: Dict[str, User]
) -> AsyncClient:
    """Create authenticated client with admin user"""
    from tests.utils.auth import create_auth_headers
    
    headers = await create_auth_headers(test_users["admin"])
    client.headers.update(headers)
    return client


@pytest_asyncio.fixture
async def user_client(
    client: AsyncClient, 
    test_users: Dict[str, User]
) -> AsyncClient:
    """Create authenticated client with regular user"""
    from tests.utils.auth import create_auth_headers
    
    headers = await create_auth_headers(test_users["user"])
    client.headers.update(headers)
    return client


@pytest_asyncio.fixture
async def approver_client(
    client: AsyncClient, 
    test_users: Dict[str, User]
) -> AsyncClient:
    """Create authenticated client with approver user"""
    from tests.utils.auth import create_auth_headers
    
    headers = await create_auth_headers(test_users["approver"])
    client.headers.update(headers)
    return client