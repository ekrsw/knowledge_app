from typing import Optional
from app.core.exceptions import DuplicateResourceError

class DuplicateUsernameError(DuplicateResourceError):
    """ユーザーの重複エラー"""
    def __init__(self, message: Optional[str] = None):
        super().__init__("User", message=message)


class DuplicateEmailError(DuplicateResourceError):
    """メールアドレスの重複エラー"""
    def __init__(self, message: Optional[str] = None):
        super().__init__("Email", message=message)

class MissingRequiredFieldError(Exception):
    """必須フィールドが不足している場合のエラー"""
    def __init__(self, field_name: Optional[str] = None, message: Optional[str] = None):
        if message is None:
            if field_name:
                message = f"{field_name} is required"
            else:
                message = "Required field is missing"
        self.field_name = field_name
        self.message = message
        super().__init__(self.message)


class DatabaseIntegrityError(Exception):
    """データベースの整合性エラー"""
    def __init__(self, message: str = "Database integrity error"):
        self.message = message
        super().__init__(self.message)


class InvalidPasswordError(Exception):
    """パスワードが無効な場合のエラー"""
    def __init__(self, message: str = "Invalid password"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """ユーザーが見つからない場合のエラー"""
    def __init__(self, identifier: str, message: Optional[str] = None):
        if message is None:
            message = "User not found"  # セキュリティ強化: 汎用的なメッセージ
        self.identifier = identifier
        self.message = message
        super().__init__(self.message)
