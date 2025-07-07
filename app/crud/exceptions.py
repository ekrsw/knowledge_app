from app.core.exceptions import DuplicateResourceError

class DuplicateUsernameError(DuplicateResourceError):
    """ユーザーの重複エラー"""
    def __init__(self, field: str = None, value = None, message: str = None):
        super().__init__("User", field, value, message)


class DuplicateEmailError(DuplicateResourceError):
    """メールアドレスの重複エラー"""
    def __init__(self, field: str = None, value = None, message: str = None):
        super().__init__("Email", field, value, message)

class DatabaseIntegrityError(Exception):
    """データベースの整合性エラー"""
    def __init__(self, message: str = "Database integrity error"):
        self.message = message
        super().__init__(self.message)