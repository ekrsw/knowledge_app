"""
Integration tests for articles API endpoints
"""
import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.factories.user_factory import UserFactory
from tests.factories.article_factory import ArticleFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.info_category_factory import InfoCategoryFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


class TestArticleIdConversion:
    """Test article ID/number conversion endpoints"""

    @pytest_asyncio.fixture
    async def test_data(self, db_session: AsyncSession):
        """Create test data for conversion tests"""
        # Create necessary entities
        approval_group = await ApprovalGroupFactory.create(
            db=db_session,
            group_name="Test Approval Group"
        )
        info_category = await InfoCategoryFactory.create(
            db=db_session,
            category_name="Test Category"
        )
        
        # Create test article with known ID and number
        article = await ArticleFactory.create(
            db=db_session,
            article_id="TEST-001",
            article_number="KB-2024-001",
            title="Test Article for Conversion",
            info_category=info_category,
            approval_group=approval_group
        )
        
        return {
            "article": article,
            "approval_group": approval_group,
            "info_category": info_category
        }
    
    async def test_get_article_id_by_number_success(
        self,
        client: AsyncClient,
        test_data: dict
    ):
        """Test getting article_id by article_number - success case"""
        article = test_data["article"]
        
        response = await client.get(f"/api/v1/articles/id-by-number/{article.article_number}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["article_id"] == article.article_id
    
    async def test_get_article_id_by_number_not_found(
        self,
        client: AsyncClient,
        test_data: dict
    ):
        """Test getting article_id by non-existent article_number"""
        non_existent_number = "KB-9999-999"
        
        response = await client.get(f"/api/v1/articles/id-by-number/{non_existent_number}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Article not found"
    
    async def test_get_article_number_by_id_success(
        self,
        client: AsyncClient,
        test_data: dict
    ):
        """Test getting article_number by article_id - success case"""
        article = test_data["article"]
        
        response = await client.get(f"/api/v1/articles/number-by-id/{article.article_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["article_number"] == article.article_number
    
    async def test_get_article_number_by_id_not_found(
        self,
        client: AsyncClient,
        test_data: dict
    ):
        """Test getting article_number by non-existent article_id"""
        non_existent_id = "NONEXISTENT-999"
        
        response = await client.get(f"/api/v1/articles/number-by-id/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Article not found"
    
    async def test_conversion_consistency(
        self,
        client: AsyncClient,
        test_data: dict
    ):
        """Test that conversions are consistent both ways"""
        article = test_data["article"]
        
        # Get ID by number
        response1 = await client.get(f"/api/v1/articles/id-by-number/{article.article_number}")
        assert response1.status_code == status.HTTP_200_OK
        retrieved_id = response1.json()["article_id"]
        
        # Get number by ID
        response2 = await client.get(f"/api/v1/articles/number-by-id/{retrieved_id}")
        assert response2.status_code == status.HTTP_200_OK
        retrieved_number = response2.json()["article_number"]
        
        # Verify consistency
        assert retrieved_id == article.article_id
        assert retrieved_number == article.article_number
    
    async def test_multiple_articles_conversion(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_data: dict
    ):
        """Test conversion with multiple articles"""
        approval_group = test_data["approval_group"]
        info_category = test_data["info_category"]
        
        # Create additional articles
        articles = []
        for i in range(3):
            article = await ArticleFactory.create(
                db=db_session,
                article_id=f"TEST-00{i+2}",
                article_number=f"KB-2024-00{i+2}",
                info_category=info_category,
                approval_group=approval_group
            )
            articles.append(article)
        
        # Test conversion for each article
        for article in articles:
            # Test ID by number
            response1 = await client.get(f"/api/v1/articles/id-by-number/{article.article_number}")
            assert response1.status_code == status.HTTP_200_OK
            assert response1.json()["article_id"] == article.article_id
            
            # Test number by ID
            response2 = await client.get(f"/api/v1/articles/number-by-id/{article.article_id}")
            assert response2.status_code == status.HTTP_200_OK
            assert response2.json()["article_number"] == article.article_number


class TestArticleIdConversionEdgeCases:
    """Test edge cases for article ID/number conversion"""
    
    @pytest_asyncio.fixture
    async def edge_case_data(self, db_session: AsyncSession):
        """Create test data with edge case scenarios"""
        approval_group = await ApprovalGroupFactory.create(db=db_session)
        info_category = await InfoCategoryFactory.create(db=db_session)
        
        # Create articles with special characters and formats
        articles = []
        
        # Article with special characters in ID
        article1 = await ArticleFactory.create(
            db=db_session,
            article_id="TEST-SPECIAL_CHARS-001",
            article_number="KB-2024-SPECIAL",
            info_category=info_category,
            approval_group=approval_group
        )
        articles.append(article1)
        
        # Article with numbers in both ID and number
        article2 = await ArticleFactory.create(
            db=db_session,
            article_id="12345-NUMERIC",
            article_number="9999-NUMERIC",
            info_category=info_category,
            approval_group=approval_group
        )
        articles.append(article2)
        
        return {
            "articles": articles,
            "approval_group": approval_group,
            "info_category": info_category
        }
    
    async def test_special_characters_in_id(
        self,
        client: AsyncClient,
        edge_case_data: dict
    ):
        """Test conversion with special characters in article_id"""
        article = edge_case_data["articles"][0]  # TEST-SPECIAL_CHARS-001
        
        # Test number by ID
        response = await client.get(f"/api/v1/articles/number-by-id/{article.article_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["article_number"] == article.article_number
        
        # Test ID by number
        response = await client.get(f"/api/v1/articles/id-by-number/{article.article_number}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["article_id"] == article.article_id
    
    async def test_numeric_strings(
        self,
        client: AsyncClient,
        edge_case_data: dict
    ):
        """Test conversion with numeric-like strings"""
        article = edge_case_data["articles"][1]  # 12345-NUMERIC
        
        # Test conversion both ways
        response1 = await client.get(f"/api/v1/articles/number-by-id/{article.article_id}")
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["article_number"] == article.article_number
        
        response2 = await client.get(f"/api/v1/articles/id-by-number/{article.article_number}")
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["article_id"] == article.article_id
    
    async def test_url_encoding_handling(
        self,
        client: AsyncClient,
        edge_case_data: dict
    ):
        """Test that URL encoding is handled properly"""
        # Test with article ID that might need URL encoding
        article = edge_case_data["articles"][0]  # TEST-SPECIAL_CHARS-001
        
        # The FastAPI client should handle URL encoding automatically
        response = await client.get(f"/api/v1/articles/number-by-id/{article.article_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["article_number"] == article.article_number