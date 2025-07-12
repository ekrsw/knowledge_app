"""Tests for core exceptions."""

import pytest
from app.core.exceptions import AppException, DuplicateResourceError


class TestAppException:
    """AppExceptionのテスト"""

    def test_init_with_message(self):
        """カスタムメッセージ付きの初期化をテスト"""
        custom_message = "Custom application error"
        error = AppException(custom_message)
        
        assert error.message == custom_message
        assert str(error) == custom_message

    def test_init_without_message(self):
        """デフォルトメッセージでの初期化をテスト"""
        error = AppException()
        
        assert error.message == "An application error occurred"
        assert str(error) == "An application error occurred"


class TestDuplicateResourceError:
    """DuplicateResourceErrorのテスト"""

    def test_init_basic(self):
        """基本的な初期化をテスト"""
        resource_type = "User"
        error = DuplicateResourceError(resource_type)
        
        assert error.resource_type == resource_type
        assert error.field is None
        assert error.value is None
        assert error.message == "Duplicate User"
        assert str(error) == "Duplicate User"

    def test_init_with_custom_message(self):
        """カスタムメッセージ付きの初期化をテスト"""
        resource_type = "Email"
        custom_message = "Email address already exists"
        error = DuplicateResourceError(resource_type, message=custom_message)
        
        assert error.resource_type == resource_type
        assert error.message == custom_message
        assert str(error) == custom_message

    def test_init_with_field_and_value(self):
        """フィールドと値を指定した初期化をテスト（Missing行17をカバー）"""
        resource_type = "User"
        field = "username"
        value = "testuser"
        error = DuplicateResourceError(resource_type, field, value)
        
        assert error.resource_type == resource_type
        assert error.field == field
        assert error.value == value
        assert error.message == "Duplicate User with username='testuser'"
        assert str(error) == "Duplicate User with username='testuser'"

    def test_init_with_field_only(self):
        """フィールドのみ指定した場合のテスト"""
        resource_type = "Product"
        field = "code"
        error = DuplicateResourceError(resource_type, field=field)
        
        assert error.resource_type == resource_type
        assert error.field == field
        assert error.value is None
        # fieldはあるがvalueがないので、詳細メッセージは作成されない
        assert error.message == "Duplicate Product"

    def test_init_with_value_only(self):
        """値のみ指定した場合のテスト"""
        resource_type = "Category"
        value = "electronics"
        error = DuplicateResourceError(resource_type, value=value)
        
        assert error.resource_type == resource_type
        assert error.field is None
        assert error.value == value
        # valueはあるがfieldがないので、詳細メッセージは作成されない
        assert error.message == "Duplicate Category"

    def test_init_with_field_value_and_custom_message(self):
        """フィールド、値、カスタムメッセージすべて指定のテスト"""
        resource_type = "Account"
        field = "email"
        value = "test@example.com"
        custom_message = "Account with this email already exists"
        error = DuplicateResourceError(resource_type, field, value, custom_message)
        
        assert error.resource_type == resource_type
        assert error.field == field
        assert error.value == value
        # カスタムメッセージが優先される
        assert error.message == custom_message
        assert str(error) == custom_message


class TestExceptionsInheritance:
    """例外の継承関係のテスト"""

    def test_app_exception_inheritance(self):
        """AppExceptionの継承関係をテスト"""
        error = AppException()
        assert isinstance(error, Exception)

    def test_duplicate_resource_error_inheritance(self):
        """DuplicateResourceErrorの継承関係をテスト"""
        error = DuplicateResourceError("Test")
        assert isinstance(error, AppException)
        assert isinstance(error, Exception)


class TestExceptionsUsage:
    """実際の使用パターンのテスト"""

    def test_raise_and_catch_app_exception(self):
        """AppExceptionの発生と捕捉をテスト"""
        with pytest.raises(AppException) as exc_info:
            raise AppException("Test error")
        
        assert "Test error" in str(exc_info.value)

    def test_raise_and_catch_duplicate_resource_error(self):
        """DuplicateResourceErrorの発生と捕捉をテスト"""
        with pytest.raises(DuplicateResourceError) as exc_info:
            raise DuplicateResourceError("User", "email", "test@example.com")
        
        assert "Duplicate User with email='test@example.com'" in str(exc_info.value)

    def test_catch_as_app_exception(self):
        """DuplicateResourceErrorをAppExceptionとして捕捉するテスト"""
        with pytest.raises(AppException) as exc_info:
            raise DuplicateResourceError("Product")
        
        assert isinstance(exc_info.value, DuplicateResourceError)
        assert "Duplicate Product" in str(exc_info.value)