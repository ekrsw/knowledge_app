from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import re
from typing import NoReturn

from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.crud.exceptions import (
    DuplicateUsernameError,
    DuplicateEmailError,
    MissingRequiredFieldError,
    DatabaseIntegrityError
)
from app.models.user import User
from app.schemas.user import UserCreate


class CRUDUser:
    # クラスレベルのロガー初期化
    logger = get_logger(__name__)
    
    def _handle_integrity_error(self, e: IntegrityError, obj_in: UserCreate) -> NoReturn:
        """IntegrityErrorを適切なカスタム例外に変換"""
        error_code = getattr(e.orig, 'pgcode', None) if hasattr(e.orig, 'pgcode') else None
        error_msg = str(e.orig).lower()
        
        self.logger.error(f"IntegrityError occurred: {str(e)}, pgcode: {error_code}")
        
        # PostgreSQLエラーコードによる詳細な判別
        if error_code == '23505':  # UNIQUE制約違反
            self._handle_unique_constraint_violation(error_msg, obj_in, e)
        elif error_code == '23502':  # NOT NULL制約違反
            self._handle_not_null_constraint_violation(e)
        else:
            # フォールバック処理
            self._handle_fallback_integrity_error(error_msg, obj_in, e)
        
        # この行に到達することはないが、型チェッカーのために追加
        raise DatabaseIntegrityError("Unhandled integrity error") from e
    
    def _handle_unique_constraint_violation(self, error_msg: str, obj_in: UserCreate, e: IntegrityError) -> NoReturn:
        """UNIQUE制約違反の処理"""
        if "username" in error_msg:
            self.logger.error(f"Failed to create user: duplicate username")
            raise DuplicateUsernameError("Username already exists") from e
        elif "email" in error_msg:
            self.logger.error(f"Failed to create user: duplicate email")
            raise DuplicateEmailError("Email already exists") from e
        else:
            self.logger.error(f"Unknown unique constraint violation: {str(e)}")
            raise DatabaseIntegrityError("Unique constraint violation") from e
    
    def _handle_not_null_constraint_violation(self, e: IntegrityError) -> NoReturn:
        """NOT NULL制約違反の処理"""
        # PostgreSQLエラーメッセージから正確にカラム名を抽出
        column_match = re.search(r'列"([^"]+)"', str(e.orig))
        if column_match:
            column_name = column_match.group(1)
            self.logger.error(f"Failed to create user: {column_name} is required but missing")
            
            # カラム名に基づいて適切なフィールド名を決定
            field_mapping = {
                "username": "username",
                "email": "email", 
                "hashed_password": "password",
                "group": "group"
            }
            
            field_name = field_mapping.get(column_name, column_name)
            raise MissingRequiredFieldError(field_name, f"{field_name.capitalize()} is required") from e
        else:
            # フォールバック: 従来の方法
            error_msg = str(e.orig).lower()
            if '"username"' in error_msg:
                self.logger.error("Failed to create user: username is required but missing")
                raise MissingRequiredFieldError("username", "Username is required") from e
            elif '"email"' in error_msg:
                self.logger.error("Failed to create user: email is required but missing")
                raise MissingRequiredFieldError("email", "Email is required") from e
            elif '"hashed_password"' in error_msg:
                self.logger.error("Failed to create user: password is required but missing")
                raise MissingRequiredFieldError("password", "Password is required") from e
            elif '"group"' in error_msg:
                self.logger.error("Failed to create user: group is required but missing")
                raise MissingRequiredFieldError("group", "Group is required") from e
            else:
                self.logger.error(f"Unknown not null constraint violation: {str(e)}")
                raise MissingRequiredFieldError(message="Required field is missing") from e
    
    def _handle_fallback_integrity_error(self, error_msg: str, obj_in: UserCreate, e: IntegrityError) -> NoReturn:
        """エラーコードが取得できない場合のフォールバック処理"""
        if "unique" in error_msg or "duplicate" in error_msg:
            if "username" in error_msg:
                self.logger.error(f"Failed to create user: duplicate username")
                raise DuplicateUsernameError("Username already exists") from e
            elif "email" in error_msg:
                self.logger.error(f"Failed to create user: duplicate email")
                raise DuplicateEmailError("Email already exists") from e
            else:
                self.logger.error(f"Unknown duplicate constraint violation: {str(e)}")
                raise DatabaseIntegrityError("Duplicate constraint violation") from e
        elif "null" in error_msg or "not-null" in error_msg:
            if "username" in error_msg:
                raise MissingRequiredFieldError("username", "Username is required") from e
            elif "email" in error_msg:
                raise MissingRequiredFieldError("email", "Email is required") from e
            else:
                raise MissingRequiredFieldError(message="Required field is missing") from e
        else:
            # その他のIntegrityErrorの場合
            self.logger.error(f"Database integrity error while creating user: {str(e)}")
            raise DatabaseIntegrityError("Database integrity error") from e

    async def create_user(self, session: AsyncSession, obj_in: UserCreate) -> User:
        """
        新しいユーザーを作成する
        
        Args:
            session: データベースセッション
            obj_in: ユーザー作成データ
            
        Returns:
            User: 作成されたユーザーオブジェクト
            
        Raises:
            DuplicateUsernameError: ユーザー名が既に存在する場合
            DuplicateEmailError: メールアドレスが既に存在する場合
            MissingRequiredFieldError: 必須フィールドが不足している場合
            DatabaseIntegrityError: その他のデータベース整合性エラー
        """
        self.logger.info(f"Creating new user with username: {obj_in.username}")
        
        try:
            db_obj = User(
                username=obj_in.username,
                email=obj_in.email,
                hashed_password=get_password_hash(obj_in.password),
                full_name=obj_in.full_name,
                ctstage_name=obj_in.ctstage_name,
                sweet_name=obj_in.sweet_name,
                group=obj_in.group,
                is_active=obj_in.is_active,
                is_admin=obj_in.is_admin,
                is_sv=obj_in.is_sv
            )
            session.add(db_obj)
            await session.flush()
            await session.commit()
            self.logger.info(f"User created successfully: {db_obj.id}")
            return db_obj
            
        except IntegrityError as e:
            await session.rollback()
            self._handle_integrity_error(e, obj_in)
            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Unexpected error creating user: {str(e)}")
            raise DatabaseIntegrityError("Failed to create user") from e

    async def get_user_by_username(self, session: AsyncSession, username: str) -> User | None:
        """
        ユーザー名でユーザーを取得する
        
        Args:
            session: データベースセッション
            username: 検索するユーザー名
            
        Returns:
            User: 見つかったユーザーオブジェクト、見つからない場合はNone
        """
        self.logger.info(f"Getting user by username: {username}")
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                self.logger.info(f"User found: {user.id}")
            else:
                self.logger.info(f"User not found with username: {username}")
                
            return user
        except Exception as e:
            self.logger.error(f"Error getting user by username '{username}': {str(e)}")
            raise

user_crud = CRUDUser()
