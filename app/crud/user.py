from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

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
    async def create_user(self, session: AsyncSession, obj_in: UserCreate) -> User:
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
            # commitはsessionのfinallyブロックで行う
            self.logger.info(f"User created successfully: {db_obj.id}")
        except IntegrityError as e:
            # PostgreSQLエラーコードとメッセージを取得
            error_code = getattr(e.orig, 'pgcode', None) if hasattr(e.orig, 'pgcode') else None
            error_msg = str(e.orig).lower()
            
            self.logger.error(f"IntegrityError occurred: {str(e)}, pgcode: {error_code}")
            
            # PostgreSQLエラーコードによる詳細な判別
            if error_code == '23505':  # UNIQUE制約違反
                if "username" in error_msg:
                    self.logger.error(f"Failed to create user: duplicate username '{obj_in.username}'")
                    raise DuplicateUsernameError("Username already exists")
                elif "email" in error_msg:
                    self.logger.error(f"Failed to create user: duplicate email '{obj_in.email}'")
                    raise DuplicateEmailError("Email already exists")
                else:
                    self.logger.error(f"Unknown unique constraint violation: {str(e)}")
                    raise DatabaseIntegrityError("Unique constraint violation") from e
                    
            elif error_code == '23502':  # NOT NULL制約違反
                # PostgreSQLエラーメッセージから正確にカラム名を抽出
                import re
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
                    raise MissingRequiredFieldError(field_name, f"{field_name.capitalize()} is required")
                else:
                    # フォールバック: 従来の方法
                    if '"username"' in str(e.orig):
                        self.logger.error("Failed to create user: username is required but missing")
                        raise MissingRequiredFieldError("username", "Username is required")
                    elif '"email"' in str(e.orig):
                        self.logger.error("Failed to create user: email is required but missing")
                        raise MissingRequiredFieldError("email", "Email is required")
                    elif '"hashed_password"' in str(e.orig):
                        self.logger.error("Failed to create user: password is required but missing")
                        raise MissingRequiredFieldError("password", "Password is required")
                    elif '"group"' in str(e.orig):
                        self.logger.error("Failed to create user: group is required but missing")
                        raise MissingRequiredFieldError("group", "Group is required")
                    else:
                        self.logger.error(f"Unknown not null constraint violation: {str(e)}")
                        raise MissingRequiredFieldError(message="Required field is missing")
                    
            else:
                # フォールバック: エラーコードが取得できない場合の従来の判別方法
                if "unique" in error_msg or "duplicate" in error_msg:
                    if "username" in error_msg:
                        self.logger.error(f"Failed to create user: duplicate username '{obj_in.username}'")
                        raise DuplicateUsernameError("Username already exists")
                    elif "email" in error_msg:
                        self.logger.error(f"Failed to create user: duplicate email '{obj_in.email}'")
                        raise DuplicateEmailError("Email already exists")
                elif "null" in error_msg or "not-null" in error_msg:
                    if "username" in error_msg:
                        raise MissingRequiredFieldError("username", "Username is required")
                    elif "email" in error_msg:
                        raise MissingRequiredFieldError("email", "Email is required")
                    else:
                        raise MissingRequiredFieldError(message="Required field is missing")
                
                # その他のIntegrityErrorの場合
                self.logger.error(f"Database integrity error while creating user: {str(e)}")
                raise DatabaseIntegrityError("Database integrity error") from e
        return db_obj

user_crud = CRUDUser()
