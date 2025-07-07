from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.logging import get_logger
from app.core.exceptions import (
    DuplicateUsernameError,
    DuplicateEmailError,
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
                hashed_password=get_password_hash(obj_in.password)
            )
            session.add(db_obj)
            await session.flush()
            # commitはsessionのfinallyブロックで行う
            self.logger.info(f"User created successfully: {db_obj.id}")
        except IntegrityError as e:
            # エラーメッセージやコードを検査して、具体的なエラータイプを特定
            if "username" in str(e.orig).lower():
                self.logger.error(f"Failed to create user: duplicate username '{obj_in.username}'")
                raise DuplicateUsernameError("Username already exists.")
            elif "email" in str(e.orig).lower():
                self.logger.error(f"Failed to create user: duplicate email '{obj_in.email}'")
                raise DuplicateEmailError("Email already exists")
            else:
                # その他のIntegrityErrorの場合
                self.logger.error(f"Database integrity error while creating user: {str(e)}")
                raise DatabaseIntegrityError("Database integrity error") from e
        return db_obj