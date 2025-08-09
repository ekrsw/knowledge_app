"""
Custom assertion utilities for tests
"""
from typing import Dict, Any, List, Optional, Union
from httpx import Response

from app.models.user import User
from app.models.revision import Revision
from app.models.article import Article


def assert_response_success(response: Response, expected_status: int = 200) -> None:
    """
    Assert that response is successful with expected status code
    
    Args:
        response: HTTP response to check
        expected_status: Expected HTTP status code
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_permission_denied(response: Response) -> None:
    """
    Assert that response indicates permission denied (403)
    
    Args:
        response: HTTP response to check
    """
    assert response.status_code == 403, (
        f"Expected 403 Forbidden, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_unauthorized(response: Response) -> None:
    """
    Assert that response indicates unauthorized (401)
    
    Args:
        response: HTTP response to check
    """
    assert response.status_code == 401, (
        f"Expected 401 Unauthorized, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_not_found(response: Response) -> None:
    """
    Assert that response indicates not found (404)
    
    Args:
        response: HTTP response to check
    """
    assert response.status_code == 404, (
        f"Expected 404 Not Found, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_validation_error(response: Response) -> None:
    """
    Assert that response indicates validation error (422)
    
    Args:
        response: HTTP response to check
    """
    assert response.status_code == 422, (
        f"Expected 422 Validation Error, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_bad_request(response: Response) -> None:
    """
    Assert that response indicates bad request (400)
    
    Args:
        response: HTTP response to check
    """
    assert response.status_code == 400, (
        f"Expected 400 Bad Request, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_user_response(response_data: Dict[str, Any], expected_user: User) -> None:
    """
    Assert that user response data matches expected user
    
    Args:
        response_data: User data from API response
        expected_user: Expected user object
    """
    assert response_data["id"] == str(expected_user.id)
    assert response_data["username"] == expected_user.username
    assert response_data["email"] == expected_user.email
    assert response_data["full_name"] == expected_user.full_name
    assert response_data["role"] == expected_user.role
    assert response_data["is_active"] == expected_user.is_active


def assert_revision_response(response_data: Dict[str, Any], expected_revision: Revision) -> None:
    """
    Assert that revision response data matches expected revision
    
    Args:
        response_data: Revision data from API response  
        expected_revision: Expected revision object
    """
    assert response_data["revision_id"] == str(expected_revision.revision_id)
    assert response_data["target_article_id"] == expected_revision.target_article_id
    assert response_data["proposer_id"] == str(expected_revision.proposer_id)
    assert response_data["approver_id"] == str(expected_revision.approver_id)
    assert response_data["status"] == expected_revision.status
    assert response_data["reason"] == expected_revision.reason


def assert_article_response(response_data: Dict[str, Any], expected_article: Article) -> None:
    """
    Assert that article response data matches expected article
    
    Args:
        response_data: Article data from API response
        expected_article: Expected article object
    """
    assert response_data["article_id"] == expected_article.article_id
    assert response_data["title"] == expected_article.title
    assert response_data["importance"] == expected_article.importance
    assert response_data["is_active"] == expected_article.is_active


def assert_paginated_response(
    response_data: Dict[str, Any], 
    expected_total: Optional[int] = None,
    expected_items_count: Optional[int] = None
) -> None:
    """
    Assert that response is a valid paginated response
    
    Args:
        response_data: Paginated response data
        expected_total: Expected total count (optional)
        expected_items_count: Expected items in current page (optional)
    """
    assert isinstance(response_data, list), "Expected list response for pagination"
    
    if expected_items_count is not None:
        assert len(response_data) == expected_items_count, (
            f"Expected {expected_items_count} items, got {len(response_data)}"
        )


def assert_error_response(
    response_data: Dict[str, Any], 
    expected_error_type: Optional[str] = None,
    expected_message_contains: Optional[str] = None
) -> None:
    """
    Assert that response is a valid error response
    
    Args:
        response_data: Error response data
        expected_error_type: Expected error type (optional)
        expected_message_contains: Text that should be in error message (optional)
    """
    assert "detail" in response_data, "Expected 'detail' field in error response"
    
    if expected_message_contains:
        detail = response_data["detail"]
        if isinstance(detail, dict):
            message = detail.get("message", "")
        else:
            message = str(detail)
        
        assert expected_message_contains.lower() in message.lower(), (
            f"Expected '{expected_message_contains}' in error message: {message}"
        )


def assert_list_contains_items(
    actual_list: List[Dict[str, Any]],
    expected_items: List[Dict[str, Any]],
    key_field: str = "id"
) -> None:
    """
    Assert that a list contains expected items (by key field)
    
    Args:
        actual_list: Actual list from response
        expected_items: Expected items to find
        key_field: Field to use for matching items
    """
    actual_keys = {item[key_field] for item in actual_list}
    expected_keys = {item[key_field] for item in expected_items}
    
    missing_keys = expected_keys - actual_keys
    assert not missing_keys, f"Missing items with {key_field}: {missing_keys}"


def assert_field_updated(
    response_data: Dict[str, Any],
    field_name: str,
    expected_value: Any
) -> None:
    """
    Assert that a specific field was updated to expected value
    
    Args:
        response_data: Response data from update operation
        field_name: Name of the field to check
        expected_value: Expected value for the field
    """
    assert field_name in response_data, f"Field '{field_name}' not in response"
    actual_value = response_data[field_name]
    assert actual_value == expected_value, (
        f"Field '{field_name}': expected {expected_value}, got {actual_value}"
    )