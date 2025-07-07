class AppException(Exception):
    """アプリケーションのベース例外クラス"""
    def __init__(self, message: str = "An application error occurred"):
        self.message = message
        super().__init__(self.message)

class DuplicateResourceError(AppException):
    """リソースの重複エラー"""
    def __init__(self, resource_type: str, field: str=None, value = None, message: str=None):
        self.resource_type = resource_type
        self.field = field
        self.value = value
        default_message = f"Duplicate {resource_type}"
        if field and value:
            default_message += f" with {field}='{value}'"
        self.message = message or default_message
        super().__init__(self.message)