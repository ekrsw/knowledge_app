"""User CRUD operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for User model.
"""

from typing import List, Optional
from uuid import UUID
import hashlib
import asyncio
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.logging import get_logger
from app.core.security import get_password_hash, verify_password
from app.crud.exceptions import (
    DatabaseIntegrityError,
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidPasswordError,
    MissingRequiredFieldError,
    UserNotFoundError,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for User model."""

    # クラスレベルのロガー初期化
    logger = get_logger(__name__)
    
    def _hash_user_id(self, user_id: UUID) -> str:
        """セキュリティ上の理由でユーザーIDをハッシュ化する."""
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:8]
    
    async def _constant_time_user_lookup(self, session: AsyncSession, lookup_func, *args) -> Optional[User]:
        """タイミング攻撃を防ぐためのユーザー検索."""
        start_time = time.time()
        user = await lookup_func(*args)
        
        # 最小実行時間を確保（50ms）
        min_time = 0.05
        elapsed = time.time() - start_time
        if elapsed < min_time:
            await asyncio.sleep(min_time - elapsed)
        
        return user

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
        self._log_operation("user creation", "start")

        # Pydanticでバリデーション済みなので、重複チェックを削除

        # TOCTOUレース条件を避けるため、事前チェックを削除
        # データベースレベルでの制約エラーを適切に処理

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
            await session.commit()
            self._log_operation("user creation", "success", user_id)
            return db_obj

        except IntegrityError as e:
            # セッションを明示的にロールバック
            await session.rollback()
            # 共通化された例外処理を使用
            self._handle_database_error(e, "user creation")
        
        except Exception as e:
            self._log_operation("user creation", "error", error_type=type(e).__name__)
            raise DatabaseIntegrityError("Failed to create user") from None

    def _extract_constraint_name(self, error_message: str) -> str:
        """エラーメッセージから制約名を抽出する.
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            str: 制約名、抽出できない場合は空文字列
        """
        import re
        # PostgreSQLの制約名を抽出するパターン
        
        # パターン1: DETAILメッセージからカラム名を抽出 (最も信頼性が高い)
        # 英語版: DETAIL: Key (email)=(test@example.com) already exists.
        constraint_pattern = r'DETAIL:.*Key \(([^)]+)\)'
        match = re.search(constraint_pattern, error_message)
        if match:
            return match.group(1)
        
        # パターン1b: DETAILメッセージからカラム名を抽出 (日本語版)
        # 日本語版: DETAIL: キー (username)=(test) は既に存在します。
        constraint_pattern_jp = r'DETAIL:.*キー \(([^)]+)\)'
        match_jp = re.search(constraint_pattern_jp, error_message)
        if match_jp:
            return match_jp.group(1)
        
        # パターン2: 制約名を直接抽出 (英語版)
        # 例: constraint "users_email_key" 
        constraint_pattern2 = r'constraint "([^"]+)"'
        match2 = re.search(constraint_pattern2, error_message)
        if match2:
            constraint_name = match2.group(1)
            # 制約名からフィールド名を推測
            if '_email' in constraint_name or 'email' in constraint_name:
                return 'email'
            elif '_username' in constraint_name or 'username' in constraint_name:
                return 'username'
            return constraint_name
        
        # パターン2b: 制約名を直接抽出 (日本語版)
        # 例: 制約"ix_users_username"に違反
        constraint_pattern2_jp = r'制約"([^"]+)"'
        match2_jp = re.search(constraint_pattern2_jp, error_message)
        if match2_jp:
            constraint_name = match2_jp.group(1)
            # 制約名からフィールド名を推測
            if '_email' in constraint_name or 'email' in constraint_name:
                return 'email'
            elif '_username' in constraint_name or 'username' in constraint_name:
                return 'username'
            return constraint_name
        
        # パターン3: エラーメッセージ内のキーワード検索（最後の手段）
        # usernameを先にチェック（emailはユーザー名の中にも含まれる可能性があるため）
        if 'username' in error_message.lower():
            return 'username'
        elif 'email' in error_message.lower():
            return 'email'
        
        return ""
    
    def _extract_column_name(self, error_message: str) -> str:
        """エラーメッセージからカラム名を抽出する.
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            str: カラム名、抽出できない場合は空文字列
        """
        import re
        # PostgreSQLのnull制約違反のカラム名を抽出
        column_pattern = r'column "([^"]+)"'
        match = re.search(column_pattern, error_message)
        if match:
            return match.group(1)
        
        return ""
    
    def _handle_database_error(self, e: IntegrityError, operation: str) -> None:
        """データベース例外を適切なアプリケーション例外に変換する.
        
        Args:
            e: SQLAlchemy IntegrityError
            operation: 実行していた操作名（ログ用）
            
        Raises:
            DuplicateUsernameError: ユーザー名重複の場合
            DuplicateEmailError: メール重複の場合
            MissingRequiredFieldError: NOT NULL制約違反の場合
            DatabaseIntegrityError: その他のデータベース整合性エラー
        """
        # PostgreSQL固有のエラーコードを処理
        error_code = getattr(e.orig, 'pgcode', None) if hasattr(e, 'orig') else None
        
        if error_code == '23505':  # unique_violation
            constraint_name = self._extract_constraint_name(str(e))
            
            if 'username' in constraint_name:
                self.logger.error(f"Duplicate username detected during {operation}")
                raise DuplicateUsernameError("Username already exists") from None
            elif 'email' in constraint_name:
                self.logger.error(f"Duplicate email detected during {operation}")
                raise DuplicateEmailError("Email already exists") from None
            else:
                self.logger.error(f"Unique constraint violation during {operation}: {constraint_name}")
                raise DatabaseIntegrityError(f"Unique constraint violation: {constraint_name}") from None
        elif error_code == '23502':  # not_null_violation
            column_name = self._extract_column_name(str(e))
            self.logger.error(f"NULL value in required column during {operation}: {column_name}")
            raise MissingRequiredFieldError(column_name, f"Column {column_name} cannot be null") from None
        else:
            self.logger.error(f"Database integrity error during {operation}")
            raise DatabaseIntegrityError("Database integrity error occurred") from None
    
    def _log_operation(self, operation: str, status: str, user_id: UUID = None, **kwargs) -> None:
        """構造化されたログを出力する.
        
        Args:
            operation: 実行した操作名
            status: 操作のステータス（start, success, error）
            user_id: 対象ユーザーID（オプション）
            **kwargs: 追加のログパラメータ
        """
        log_data = {
            "operation": operation,
            "status": status
        }
        
        if user_id:
            log_data["user_id_hash"] = self._hash_user_id(user_id)
        
        # 追加パラメータをマージ
        log_data.update(kwargs)
        
        # ログレベルに応じて出力
        if status == "start":
            self.logger.info(f"{operation.title()} started", extra=log_data)
        elif status == "success":
            self.logger.info(f"{operation.title()} completed successfully", extra=log_data)
        elif status == "error":
            self.logger.error(f"{operation.title()} failed", extra=log_data)
        else:
            self.logger.debug(f"{operation.title()} - {status}", extra=log_data)
    

    # _check_unique_constraintsメソッドを削除
    # TOCTOUレース条件を避けるため、事前チェックを廃止し
    # データベースレベルでの制約エラーで適切に処理

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
        self.logger.debug("Getting user by username")
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(f"User found: {self._hash_user_id(user.id)}")
            else:
                self.logger.debug("User not found with username")

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
        self.logger.debug("Getting user by email")
        try:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(f"User found: {self._hash_user_id(user.id)}")
            else:
                self.logger.debug("User not found with email")

            return user
        except Exception as e:
            self.logger.error(
                f"Error getting user by email '{email}': {str(e)}"
            )
            raise

    async def get_user_by_id(
        self, 
        session: AsyncSession, 
        user_id: UUID
    ) -> Optional[User]:
        """IDでユーザーを取得する.

        Args:
            session: データベースセッション
            user_id: 検索するユーザーID（UUID）

        Returns:
            Optional[User]: 見つかったユーザーオブジェクト、見つからない場合はNone

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug(f"Getting user by ID: {self._hash_user_id(user_id)}")
        try:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(f"User found: {self._hash_user_id(user.id)}")
            else:
                self.logger.debug("User not found with ID")

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
        user_id: UUID,
        obj_in: UserUpdate
    ) -> User:
        """IDでユーザーを更新する.

        Args:
            session: データベースセッション
            user_id: 更新するユーザーID（UUID）
            obj_in: 更新データ

        Returns:
            User: 更新されたユーザーオブジェクト

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
            DuplicateUsernameError: ユーザー名が既に存在する場合
            DuplicateEmailError: メールアドレスが既に存在する場合
            DatabaseIntegrityError: その他のデータベース整合性エラー
        """
        self._log_operation("user update", "start", user_id)

        # 更新するユーザーの存在確認
        user = await self.get_user_by_id(session, user_id)
        if not user:
            self.logger.error("User not found for update")
            raise UserNotFoundError(user_id)

        # 更新データの取得（None値は除外）
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if not update_data:
            self.logger.debug(f"No update data provided for user: {user_id}")
            return user

        # TOCTOUレース条件を避けるため、事前チェックを削除
        # データベースレベルでの制約エラーを適切に処理

        try:
            # フィールドの更新
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            await session.flush()
            # flush後にIDを取得（commitする前）
            updated_user_id = user.id
            await session.commit()
            self._log_operation("user update", "success", updated_user_id)
            return user

        except IntegrityError as e:
            # セッションを明示的にロールバック
            await session.rollback()
            # 共通化された例外処理を使用
            self._handle_database_error(e, "user update")
        
        except Exception as e:
            self._log_operation("user update", "error", user_id, error_type=type(e).__name__)
            raise DatabaseIntegrityError("Failed to update user") from None

    # _check_unique_constraints_for_updateメソッドを削除
    # TOCTOUレース条件を避けるため、事前チェックを廃止し
    # データベースレベルでの制約エラーで適切に処理

    async def update_password(
        self,
        session: AsyncSession,
        user_id: UUID,
        old_password: str,
        new_password: str
    ) -> User:
        """ユーザーのパスワードを更新する.

        Args:
            session: データベースセッション
            user_id: 更新するユーザーID（UUID）
            old_password: 現在のパスワード
            new_password: 新しいパスワード

        Returns:
            User: 更新されたユーザーオブジェクト

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
            InvalidPasswordError: 現在のパスワードが正しくない場合
            MissingRequiredFieldError: 必須パラメータが不足している場合
            DatabaseIntegrityError: その他のデータベース整合性エラー
        """
        self._log_operation("password update", "start", user_id)

        # 入力パラメータの検証
        if not old_password or not old_password.strip():
            self.logger.error("Failed to update password: old_password is required")
            raise MissingRequiredFieldError("old_password", "Old password is required")

        if not new_password or not new_password.strip():
            self.logger.error("Failed to update password: new_password is required")
            raise MissingRequiredFieldError("new_password", "New password is required")

        # 更新するユーザーの存在確認
        user = await self.get_user_by_id(session, user_id)
        if not user:
            self.logger.error("User not found for password update")
            raise UserNotFoundError(user_id)

        # 現在のパスワードの検証（タイミング攻撃対策）
        start_time = time.time()
        is_valid = verify_password(old_password, user.hashed_password)
        
        # 最小実行時間を確保（250ms）
        min_time = 0.25
        elapsed = time.time() - start_time
        if elapsed < min_time:
            await asyncio.sleep(min_time - elapsed)
        
        if not is_valid:
            self.logger.error("Invalid old password for user")
            raise InvalidPasswordError("Current password is incorrect")

        try:
            # 新しいパスワードのハッシュ化と更新
            user.hashed_password = get_password_hash(new_password)

            await session.flush()
            # flush後にIDを取得（commitする前）
            updated_user_id = user.id
            await session.commit()
            self._log_operation("password update", "success", updated_user_id)
            return user

        except Exception as e:
            self.logger.error("Unexpected error updating password")
            raise DatabaseIntegrityError("Failed to update password") from None

    async def delete_user(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> User:
        """IDでユーザーを削除する.

        Args:
            session: データベースセッション
            user_id: 削除するユーザーID（UUID）

        Returns:
            User: 削除されたユーザーオブジェクト

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
            DatabaseIntegrityError: その他のデータベース整合性エラー
        """
        self._log_operation("user deletion", "start", user_id)

        # 削除するユーザーの存在確認
        user = await self.get_user_by_id(session, user_id)
        if not user:
            self.logger.error("User not found for deletion")
            raise UserNotFoundError(user_id)

        try:
            await session.delete(user)
            await session.flush()
            # flush後にIDを取得（commitする前）
            deleted_user_id = user.id
            await session.commit()
            self._log_operation("user deletion", "success", deleted_user_id)
            return user

        except Exception as e:
            self.logger.error("Unexpected error deleting user")
            raise DatabaseIntegrityError("Failed to delete user") from None


user_crud = CRUDUser()
