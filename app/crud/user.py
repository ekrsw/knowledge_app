"""User CRUD operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for User model.
"""

from typing import List, Optional
from uuid import UUID
import hashlib
import asyncio
import time
import math
from contextlib import asynccontextmanager

from sqlalchemy import select, func
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
from app.models.user import User, GroupEnum
from app.schemas.user import UserCreate, UserUpdate, PaginationParams, PaginatedUsers


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
                self.logger.error(
                    "Duplicate username detected",
                    extra={
                        "operation": operation,
                        "error_type": "duplicate_username",
                        "constraint": "username"
                    }
                )
                raise DuplicateUsernameError("Username already exists") from None
            elif 'email' in constraint_name:
                self.logger.error(
                    "Duplicate email detected",
                    extra={
                        "operation": operation,
                        "error_type": "duplicate_email",
                        "constraint": "email"
                    }
                )
                raise DuplicateEmailError("Email already exists") from None
            else:
                self.logger.error(
                    "Unique constraint violation",
                    extra={
                        "operation": operation,
                        "error_type": "unique_violation",
                        "constraint": constraint_name
                    }
                )
                raise DatabaseIntegrityError(f"Unique constraint violation: {constraint_name}") from None
        elif error_code == '23502':  # not_null_violation
            column_name = self._extract_column_name(str(e))
            self.logger.error(
                "NULL value in required column",
                extra={
                    "operation": operation,
                    "error_type": "not_null_violation",
                    "column": column_name
                }
            )
            raise MissingRequiredFieldError(column_name, f"Column {column_name} cannot be null") from None
        else:
            self.logger.error(
                "Database integrity error",
                extra={
                    "operation": operation,
                    "error_type": "database_integrity_error"
                }
            )
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
    
    @asynccontextmanager
    async def _monitor_query_performance(self, query_name: str, **context):
        """クエリのパフォーマンスを監視する.
        
        Args:
            query_name: クエリの名前
            **context: 追加のコンテキスト情報
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Query started: {query_name}", extra={"query_name": query_name, **context})
            yield
            
        finally:
            execution_time = time.time() - start_time
            
            # パフォーマンスログ
            log_data = {
                "query_name": query_name,
                "execution_time_ms": round(execution_time * 1000, 2),
                **context
            }
            
            # スローログ警告（500ms以上）
            if execution_time > 0.5:
                self.logger.warning(f"Slow query detected: {query_name}", extra=log_data)
            # 通常のパフォーマンスログ（100ms以上）
            elif execution_time > 0.1:
                self.logger.info(f"Query performance: {query_name}", extra=log_data)
            else:
                self.logger.debug(f"Query completed: {query_name}", extra=log_data)
    

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
        self.logger.debug(
            "User lookup initiated",
            extra={
                "operation": "get_user_by_username",
                "lookup_type": "username"
            }
        )
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(
                    "User found",
                    extra={
                        "operation": "get_user_by_username",
                        "lookup_type": "username",
                        "user_id_hash": self._hash_user_id(user.id)
                    }
                )
            else:
                self.logger.debug(
                    "User not found",
                    extra={
                        "operation": "get_user_by_username",
                        "lookup_type": "username",
                        "result": "not_found"
                    }
                )

            return user
        except Exception as e:
            self.logger.error(
                "Error getting user by username",
                extra={
                    "operation": "get_user_by_username",
                    "error_type": type(e).__name__,
                    "lookup_type": "username"
                }
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
        self.logger.debug(
            "User lookup initiated",
            extra={
                "operation": "get_user_by_email",
                "lookup_type": "email"
            }
        )
        try:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(
                    "User found",
                    extra={
                        "operation": "get_user_by_email",
                        "lookup_type": "email",
                        "user_id_hash": self._hash_user_id(user.id)
                    }
                )
            else:
                self.logger.debug(
                    "User not found",
                    extra={
                        "operation": "get_user_by_email",
                        "lookup_type": "email",
                        "result": "not_found"
                    }
                )

            return user
        except Exception as e:
            self.logger.error(
                "Error getting user by email",
                extra={
                    "operation": "get_user_by_email",
                    "error_type": type(e).__name__,
                    "lookup_type": "email"
                }
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
        self.logger.debug(
            "User lookup initiated",
            extra={
                "operation": "get_user_by_id",
                "lookup_type": "id",
                "user_id_hash": self._hash_user_id(user_id)
            }
        )
        try:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                self.logger.debug(
                    "User found",
                    extra={
                        "operation": "get_user_by_id",
                        "lookup_type": "id",
                        "user_id_hash": self._hash_user_id(user.id)
                    }
                )
            else:
                self.logger.debug(
                    "User not found",
                    extra={
                        "operation": "get_user_by_id",
                        "lookup_type": "id",
                        "result": "not_found"
                    }
                )

            return user
        except Exception as e:
            self.logger.error(
                "Error getting user by ID",
                extra={
                    "operation": "get_user_by_id",
                    "error_type": type(e).__name__,
                    "user_id_hash": self._hash_user_id(user_id),
                    "lookup_type": "id"
                }
            )
            raise

    async def get_all_users(
        self, 
        session: AsyncSession,
        pagination: Optional[PaginationParams] = None
    ) -> List[User]:
        """すべてのユーザーを取得する（ページネーション対応）.

        Args:
            session: データベースセッション
            pagination: ページネーションパラメータ（指定しない場合は全件取得）

        Returns:
            List[User]: ユーザーオブジェクトのリスト、ユーザーがいない場合は空リスト

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        if pagination:
            self.logger.debug(
                "Getting users with pagination",
                extra={
                    "operation": "get_all_users",
                    "pagination": True,
                    "page": pagination.page,
                    "limit": pagination.limit
                }
            )
        else:
            self.logger.debug(
                "Getting all users without pagination",
                extra={
                    "operation": "get_all_users",
                    "pagination": False
                }
            )
        
        try:
            stmt = select(User)
            
            if pagination:
                # LIMIT と OFFSET を適用
                stmt = stmt.limit(pagination.limit).offset(pagination.offset)
            
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            self.logger.debug(
                "Users retrieved",
                extra={
                    "operation": "get_all_users",
                    "count": len(users),
                    "pagination": bool(pagination)
                }
            )
            return list(users)
        except Exception as e:
            self.logger.error(
                "Error getting users",
                extra={
                    "operation": "get_all_users",
                    "error_type": type(e).__name__
                }
            )
            raise

    async def get_users_paginated(
        self, 
        session: AsyncSession,
        pagination: PaginationParams
    ) -> PaginatedUsers:
        """ページネーション付きでユーザーを取得する.

        Args:
            session: データベースセッション
            pagination: ページネーションパラメータ

        Returns:
            PaginatedUsers: ページネーション情報付きのユーザーリスト

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug(
            "Getting paginated users",
            extra={
                "operation": "get_users_paginated",
                "page": pagination.page,
                "limit": pagination.limit
            }
        )
        
        try:
            # 総数を取得（パフォーマンス監視付き）
            async with self._monitor_query_performance(
                "count_users", 
                operation="count_total_users"
            ):
                count_stmt = select(func.count(User.id))
                count_result = await session.execute(count_stmt)
                total = count_result.scalar()
            
            # ページネーション付きでユーザーを取得（パフォーマンス監視付き）
            async with self._monitor_query_performance(
                "paginated_users", 
                operation="get_paginated_users",
                page=pagination.page,
                limit=pagination.limit,
                offset=pagination.offset
            ):
                users = await self.get_all_users(session, pagination)
            
            # ページネーション情報を計算
            pages = math.ceil(total / pagination.limit) if total > 0 else 0
            has_next = pagination.page < pages
            has_prev = pagination.page > 1
            
            # User オブジェクトを辞書に変換
            users_dict = []
            for user in users:
                user_dict = {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "ctstage_name": user.ctstage_name,
                    "sweet_name": user.sweet_name,
                    "group": user.group.value if user.group else None,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "is_sv": user.is_sv,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                users_dict.append(user_dict)
            
            result = PaginatedUsers(
                users=users_dict,
                total=total,
                page=pagination.page,
                limit=pagination.limit,
                pages=pages,
                has_next=has_next,
                has_prev=has_prev
            )
            
            self.logger.debug(
                "Paginated users returned",
                extra={
                    "operation": "get_users_paginated",
                    "total": total,
                    "page": pagination.page,
                    "pages": pages
                }
            )
            return result
            
        except Exception as e:
            self.logger.error(
                "Error getting paginated users",
                extra={
                    "operation": "get_users_paginated",
                    "error_type": type(e).__name__
                }
            )
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
            self.logger.error(
                "User not found for update",
                extra={
                    "operation": "update_user_by_id",
                    "error_type": "user_not_found",
                    "user_id_hash": self._hash_user_id(user_id)
                }
            )
            raise UserNotFoundError(user_id)

        # 更新データの取得（None値は除外）
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if not update_data:
            self.logger.debug(
                "No update data provided",
                extra={
                    "operation": "update_user_by_id",
                    "user_id_hash": self._hash_user_id(user_id),
                    "reason": "empty_update_data"
                }
            )
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
            self.logger.error(
                "Failed to update password: old_password is required",
                extra={
                    "operation": "update_password",
                    "error_type": "missing_required_field",
                    "field": "old_password"
                }
            )
            raise MissingRequiredFieldError("old_password", "Old password is required")

        if not new_password or not new_password.strip():
            self.logger.error(
                "Failed to update password: new_password is required",
                extra={
                    "operation": "update_password",
                    "error_type": "missing_required_field",
                    "field": "new_password"
                }
            )
            raise MissingRequiredFieldError("new_password", "New password is required")

        # 更新するユーザーの存在確認
        user = await self.get_user_by_id(session, user_id)
        if not user:
            self.logger.error(
                "User not found for password update",
                extra={
                    "operation": "update_password",
                    "error_type": "user_not_found",
                    "user_id_hash": self._hash_user_id(user_id)
                }
            )
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
            self.logger.error(
                "Invalid old password for user",
                extra={
                    "operation": "update_password",
                    "error_type": "invalid_password",
                    "user_id_hash": self._hash_user_id(user_id)
                }
            )
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
            self.logger.error(
                "Unexpected error updating password",
                extra={
                    "operation": "update_password",
                    "error_type": "unexpected_error",
                    "user_id_hash": self._hash_user_id(user_id)
                }
            )
            raise DatabaseIntegrityError("Failed to update password") from None

    async def delete_user_by_id(
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
            self.logger.error(
                "User not found for deletion",
                extra={
                    "operation": "delete_user_by_id",
                    "error_type": "user_not_found",
                    "user_id_hash": self._hash_user_id(user_id)
                }
            )
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
            self.logger.error(
                "Unexpected error deleting user",
                extra={
                    "operation": "delete_user_by_id",
                    "error_type": "unexpected_error",
                    "user_id_hash": self._hash_user_id(user_id)
                }
            )
            raise DatabaseIntegrityError("Failed to delete user") from None

    # Backward compatibility alias
    delete_user = delete_user_by_id

    async def get_active_users(
        self,
        session: AsyncSession,
        pagination: Optional[PaginationParams] = None
    ) -> List[User]:
        """アクティブなユーザーのみを取得する（is_activeインデックス活用）.

        Args:
            session: データベースセッション
            pagination: ページネーションパラメータ（オプション）

        Returns:
            List[User]: アクティブなユーザーのリスト

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        if pagination:
            self.logger.debug(
                "Getting active users with pagination",
                extra={
                    "operation": "get_active_users",
                    "pagination": True,
                    "page": pagination.page,
                    "limit": pagination.limit
                }
            )
        else:
            self.logger.debug(
                "Getting all active users",
                extra={
                    "operation": "get_active_users",
                    "pagination": False
                }
            )
        
        try:
            async with self._monitor_query_performance(
                "get_active_users",
                operation="filter_active_users",
                pagination=bool(pagination)
            ):
                stmt = select(User).where(User.is_active == True)
                
                if pagination:
                    stmt = stmt.limit(pagination.limit).offset(pagination.offset)
                
                result = await session.execute(stmt)
                users = result.scalars().all()
                
                self.logger.debug(
                    "Active users retrieved",
                    extra={
                        "operation": "get_active_users",
                        "count": len(users),
                        "pagination": bool(pagination)
                    }
                )
                return list(users)
                
        except Exception as e:
            self.logger.error(
                "Error getting active users",
                extra={
                    "operation": "get_active_users",
                    "error_type": type(e).__name__
                }
            )
            raise

    async def get_users_by_group(
        self,
        session: AsyncSession,
        group: GroupEnum,
        pagination: Optional[PaginationParams] = None
    ) -> List[User]:
        """指定されたグループのユーザーを取得する（groupインデックス活用）.

        Args:
            session: データベースセッション
            group: 検索するグループ
            pagination: ページネーションパラメータ（オプション）

        Returns:
            List[User]: 指定グループのユーザーのリスト

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        if pagination:
            self.logger.debug(
                "Getting users by group with pagination",
                extra={
                    "operation": "get_users_by_group",
                    "group": group.value,
                    "pagination": True,
                    "page": pagination.page,
                    "limit": pagination.limit
                }
            )
        else:
            self.logger.debug(
                "Getting all users by group",
                extra={
                    "operation": "get_users_by_group",
                    "group": group.value,
                    "pagination": False
                }
            )
        
        try:
            async with self._monitor_query_performance(
                "get_users_by_group",
                operation="filter_by_group",
                group=group.value,
                pagination=bool(pagination)
            ):
                stmt = select(User).where(User.group == group)
                
                if pagination:
                    stmt = stmt.limit(pagination.limit).offset(pagination.offset)
                
                result = await session.execute(stmt)
                users = result.scalars().all()
                
                self.logger.debug(
                    "Users by group retrieved",
                    extra={
                        "operation": "get_users_by_group",
                        "group": group.value,
                        "count": len(users),
                        "pagination": bool(pagination)
                    }
                )
                return list(users)
                
        except Exception as e:
            self.logger.error(
                "Error getting users by group",
                extra={
                    "operation": "get_users_by_group",
                    "error_type": type(e).__name__,
                    "group": group.value
                }
            )
            raise

    async def get_recent_users(
        self,
        session: AsyncSession,
        limit: int = 10,
        active_only: bool = False
    ) -> List[User]:
        """最新のユーザーを取得する（created_atインデックス活用）.

        Args:
            session: データベースセッション
            limit: 取得する件数（デフォルト: 10）
            active_only: アクティブユーザーのみか（デフォルト: False）

        Returns:
            List[User]: 最新のユーザーのリスト（作成日時降順）

        Raises:
            Exception: データベースアクセスエラーが発生した場合
        """
        self.logger.debug(
            "Getting recent users",
            extra={
                "operation": "get_recent_users",
                "limit": limit,
                "active_only": active_only
            }
        )
        
        try:
            async with self._monitor_query_performance(
                "get_recent_users",
                operation="get_recent_users",
                limit=limit,
                active_only=active_only
            ):
                stmt = select(User)
                
                # アクティブユーザーのみの場合は複合インデックスを活用
                if active_only:
                    stmt = stmt.where(User.is_active == True)
                
                # created_at降順でソート（インデックス活用）
                stmt = stmt.order_by(User.created_at.desc()).limit(limit)
                
                result = await session.execute(stmt)
                users = result.scalars().all()
                
                self.logger.debug(
                    "Recent users retrieved",
                    extra={
                        "operation": "get_recent_users",
                        "count": len(users),
                        "limit": limit,
                        "active_only": active_only
                    }
                )
                return list(users)
                
        except Exception as e:
            self.logger.error(
                "Error getting recent users",
                extra={
                    "operation": "get_recent_users",
                    "error_type": type(e).__name__
                }
            )
            raise


user_crud = CRUDUser()
