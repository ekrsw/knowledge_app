"""Tests for CRUD exceptions."""

import pytest
from app.crud.exceptions import (
    DuplicateUsernameError,
    DuplicateEmailError,
    MissingRequiredFieldError,
    DatabaseIntegrityError,
)


class TestDuplicateUsernameError:
    """DuplicateUsernameErrorのテスト"""

    def test_init_with_message(self):
        """カスタムメッセージ付きの初期化をテスト"""
        custom_message = "Custom username error"
        error = DuplicateUsernameError(custom_message)
        
        assert str(error) == "Custom username error"
        assert error.message == "Custom username error"

    def test_init_without_message(self):
        """デフォルトメッセージでの初期化をテスト"""
        error = DuplicateUsernameError()
        
        assert str(error) == "Duplicate User"
        assert error.message == "Duplicate User"


class TestDuplicateEmailError:
    """DuplicateEmailErrorのテスト"""

    def test_init_with_message(self):
        """カスタムメッセージ付きの初期化をテスト"""
        custom_message = "Custom email error"
        error = DuplicateEmailError(custom_message)
        
        assert str(error) == "Custom email error"
        assert error.message == "Custom email error"

    def test_init_without_message(self):
        """デフォルトメッセージでの初期化をテスト"""
        error = DuplicateEmailError()
        
        assert str(error) == "Duplicate Email"
        assert error.message == "Duplicate Email"


class TestMissingRequiredFieldError:
    """MissingRequiredFieldErrorのテスト"""

    def test_init_with_field_name_and_message(self):
        """フィールド名とメッセージ両方指定のテスト"""
        field_name = "username"
        custom_message = "Username field is missing"
        error = MissingRequiredFieldError(field_name, custom_message)
        
        assert error.field_name == field_name
        assert error.message == custom_message
        assert str(error) == custom_message

    def test_init_with_field_name_only(self):
        """フィールド名のみ指定のテスト（メッセージ自動生成）"""
        field_name = "email"
        error = MissingRequiredFieldError(field_name)
        
        assert error.field_name == field_name
        assert error.message == "email is required"
        assert str(error) == "email is required"

    def test_init_with_message_only(self):
        """メッセージのみ指定のテスト"""
        custom_message = "Custom required field message"
        error = MissingRequiredFieldError(message=custom_message)
        
        assert error.field_name is None
        assert error.message == custom_message
        assert str(error) == custom_message

    def test_init_with_neither_field_nor_message(self):
        """フィールド名もメッセージも指定しない場合のテスト"""
        error = MissingRequiredFieldError()
        
        assert error.field_name is None
        assert error.message == "Required field is missing"
        assert str(error) == "Required field is missing"

    def test_init_with_field_name_none_and_no_message(self):
        """field_name=Noneで明示的に指定した場合のテスト"""
        error = MissingRequiredFieldError(field_name=None)
        
        assert error.field_name is None
        assert error.message == "Required field is missing"
        assert str(error) == "Required field is missing"


class TestDatabaseIntegrityError:
    """DatabaseIntegrityErrorのテスト"""

    def test_init_with_message(self):
        """カスタムメッセージ付きの初期化をテスト"""
        custom_message = "Foreign key constraint violation"
        error = DatabaseIntegrityError(custom_message)
        
        assert error.message == custom_message
        assert str(error) == custom_message

    def test_init_without_message(self):
        """デフォルトメッセージでの初期化をテスト"""
        error = DatabaseIntegrityError()
        
        assert error.message == "Database integrity error"
        assert str(error) == "Database integrity error"


class TestExceptionsInheritance:
    """例外の継承関係のテスト"""

    def test_duplicate_username_error_inheritance(self):
        """DuplicateUsernameErrorの継承関係をテスト"""
        error = DuplicateUsernameError()
        
        # DuplicateResourceErrorを継承していることを確認
        from app.core.exceptions import DuplicateResourceError
        assert isinstance(error, DuplicateResourceError)
        assert isinstance(error, Exception)

    def test_duplicate_email_error_inheritance(self):
        """DuplicateEmailErrorの継承関係をテスト"""
        error = DuplicateEmailError()
        
        # DuplicateResourceErrorを継承していることを確認
        from app.core.exceptions import DuplicateResourceError
        assert isinstance(error, DuplicateResourceError)
        assert isinstance(error, Exception)

    def test_missing_required_field_error_inheritance(self):
        """MissingRequiredFieldErrorの継承関係をテスト"""
        error = MissingRequiredFieldError()
        
        # 直接Exceptionを継承していることを確認
        assert isinstance(error, Exception)

    def test_database_integrity_error_inheritance(self):
        """DatabaseIntegrityErrorの継承関係をテスト"""
        error = DatabaseIntegrityError()
        
        # 直接Exceptionを継承していることを確認
        assert isinstance(error, Exception)


class TestExceptionsUsage:
    """実際の使用パターンのテスト"""

    def test_raise_and_catch_duplicate_username_error(self):
        """DuplicateUsernameErrorの発生と捕捉をテスト"""
        with pytest.raises(DuplicateUsernameError) as exc_info:
            raise DuplicateUsernameError("Username already exists")
        
        assert "Username already exists" in str(exc_info.value)

    def test_raise_and_catch_missing_required_field_error(self):
        """MissingRequiredFieldErrorの発生と捕捉をテスト"""
        field_name = "password"
        
        with pytest.raises(MissingRequiredFieldError) as exc_info:
            raise MissingRequiredFieldError(field_name)
        
        assert exc_info.value.field_name == field_name
        assert "password is required" in str(exc_info.value)

    def test_raise_and_catch_database_integrity_error(self):
        """DatabaseIntegrityErrorの発生と捕捉をテスト"""
        with pytest.raises(DatabaseIntegrityError) as exc_info:
            raise DatabaseIntegrityError("Constraint violation")
        
        assert "Constraint violation" in str(exc_info.value)