"""User CRUD operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for User model.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.crud.exceptions import (
    DatabaseIntegrityError,
    DuplicateEmailError,
    DuplicateUsernameError,
    MissingRequiredFieldError,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for User model."""

    # クラスレベルのロガー初期化
    logger = get_logger(__name__)

    async def create_user(
        self, 
        session: AsyncSession, 
        obj_in: UserCreate
    ) -> User:
        """新しいユーザーを作成する.

        事前チェック方式により、データベース固有のエラーコードに依存せず、
        移植性の高いエラーハンドリングを実現します。

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

        # 必須フィールドの事前チェック
        self._validate_required_fields(obj_in)

        # ユニーク制約の事前チェック
        await self._check_unique_constraints(session, obj_in)

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
            # flush後にIDを取得（commitする前）
            user_id = db_obj.id
            self.logger.info(f"User created successfully: {user_id}")
            return db_obj

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Unexpected error creating user: {str(e)}")
            raise DatabaseIntegrityError("Failed to create user") from e

    def _validate_required_fields(self, obj_in: UserCreate) -> None:
        """必須フィールドの検証.

        Args:
            obj_in: ユーザー作成データ

        Raises:
            MissingRequiredFieldError: 必須フィールドが不足している場合
        """
        if not obj_in.username or not obj_in.username.strip():
            self.logger.error("Failed to create user: username is required")
            raise MissingRequiredFieldError("username", "Username is required")

        if not obj_in.email or not obj_in.email.strip():
            self.logger.error("Failed to create user: email is required")
            raise MissingRequiredFieldError("email", "Email is required")

        if not obj_in.password or not obj_in.password.strip():
            self.logger.error("Failed to create user: password is required")
            raise MissingRequiredFieldError("password", "Password is required")

        if obj_in.group is None:
            self.logger.error("Failed to create user: group is required")
            raise MissingRequiredFieldError("group", "Group is required")

    async def _check_unique_constraints(
        self, 
        session: AsyncSession, 
        obj_in: UserCreate
    ) -> None:
        """ユニーク制約の事前チェック.

        Args:
            session: データベースセッション
            obj_in: ユーザー作成データ

        Raises:
            DuplicateUsernameError: ユーザー名が既に存在する場合
            DuplicateEmailError: メールアドレスが既に存在する場合
        """
        # ユーザー名の重複チェック
        existing_user = await self.get_user_by_username(session, obj_in.username)
        if existing_user:
            self.logger.error("Failed to create user: duplicate username")
            raise DuplicateUsernameError("Username already exists")

        # メールアドレスの重複チェック
        existing_email = await self.get_user_by_email(session, obj_in.email)
        if existing_email:
            self.logger.error("Failed to create user: duplicate email")
            raise DuplicateEmailError("Email already exists")

    async def get_user_by_username(
        self, 
        session: AsyncSession, 
        username: str
    ) -> Optional[User]:
        """ユーザー名でユーザーを取得する.

        Args:
            session: データベースセッション
            username: 検索するユーザー名

        Returns:
            Optional[User]: 見つかったユーザーオブジェクト、見つからない場合はNone

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug(f"Getting user by username: {username}")
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(f"User found: {user.id}")
            else:
                self.logger.debug(f"User not found with username: {username}")

            return user
        except Exception as e:
            self.logger.error(
                f"Error getting user by username '{username}': {str(e)}"
            )
            raise

    async def get_user_by_email(
        self, 
        session: AsyncSession, 
        email: str
    ) -> Optional[User]:
        """メールアドレスでユーザーを取得する.

        Args:
            session: データベースセッション
            email: 検索するメールアドレス

        Returns:
            Optional[User]: 見つかったユーザーオブジェクト、見つからない場合はNone

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug(f"Getting user by email: {email}")
        try:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(f"User found: {user.id}")
            else:
                self.logger.debug(f"User not found with email: {email}")

            return user
        except Exception as e:
            self.logger.error(
                f"Error getting user by email '{email}': {str(e)}"
            )
            raise

    async def get_user_by_id(
        self, 
        session: AsyncSession, 
        user_id: str
    ) -> Optional[User]:
        """IDでユーザーを取得する.

        Args:
            session: データベースセッション
            user_id: 検索するユーザーID（UUID文字列）

        Returns:
            Optional[User]: 見つかったユーザーオブジェクト、見つからない場合はNone

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug(f"Getting user by ID: {user_id}")
        try:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(f"User found: {user.id}")
            else:
                self.logger.debug(f"User not found with ID: {user_id}")

            return user
        except Exception as e:
            self.logger.error(
                f"Error getting user by ID '{user_id}': {str(e)}"
            )
            raise

    async def get_all_users(
        self, 
        session: AsyncSession
    ) -> List[User]:
        """すべてのユーザーを取得する.

        Args:
            session: データベースセッション

        Returns:
            List[User]: すべてのユーザーオブジェクトのリスト、ユーザーがいない場合は空リスト

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug("Getting all users")
        try:
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            self.logger.debug(f"Found {len(users)} users")
            return list(users)
        except Exception as e:
            self.logger.error(f"Error getting all users: {str(e)}")
            raise

    async def update_user_by_id(
        self,
        session: AsyncSession,
        user_id: str,
        obj_in: UserUpdate
    ) -> Optional[User]:
        """IDでユーザーを更新する.

        Args:
            session: データベースセッション
            user_id: 更新するユーザーID（UUID文字列）
            obj_in: 更新データ

        Returns:
            Optional[User]: 更新されたユーザーオブジェクト、見つからない場合はNone

        Raises:
            DuplicateUsernameError: ユーザー名が既に存在する場合
            DuplicateEmailError: メールアドレスが既に存在する場合
            DatabaseIntegrityError: その他のデータベース整合性エラー
        """
        self.logger.info(f"Updating user with ID: {user_id}")

        # 更新するユーザーの存在確認
        user = await self.get_user_by_id(session, user_id)
        if not user:
            self.logger.warning(f"User not found for update: {user_id}")
            return None

        # 更新データの取得（None値は除外）
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if not update_data:
            self.logger.debug(f"No update data provided for user: {user_id}")
            return user

        # ユニーク制約のチェック（更新される場合のみ）
        await self._check_unique_constraints_for_update(session, user_id, update_data)

        try:
            # フィールドの更新
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            await session.flush()
            # flush後にIDを取得（commitする前）
            updated_user_id = user.id
            self.logger.info(f"User updated successfully: {updated_user_id}")
            return user

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Unexpected error updating user: {str(e)}")
            raise DatabaseIntegrityError("Failed to update user") from e

    async def _check_unique_constraints_for_update(
        self,
        session: AsyncSession,
        user_id: str,
        update_data: dict
    ) -> None:
        """更新時のユニーク制約チェック.

        Args:
            session: データベースセッション
            user_id: 更新するユーザーID
            update_data: 更新データ

        Raises:
            DuplicateUsernameError: ユーザー名が既に存在する場合
            DuplicateEmailError: メールアドレスが既に存在する場合
        """
        # ユーザー名の重複チェック
        if "username" in update_data:
            existing_user = await self.get_user_by_username(session, update_data["username"])
            if existing_user and str(existing_user.id) != user_id:
                self.logger.error("Failed to update user: duplicate username")
                raise DuplicateUsernameError("Username already exists")

        # メールアドレスの重複チェック
        if "email" in update_data:
            existing_email = await self.get_user_by_email(session, update_data["email"])
            if existing_email and str(existing_email.id) != user_id:
                self.logger.error("Failed to update user: duplicate email")
                raise DuplicateEmailError("Email already exists")


user_crud = CRUDUser()
