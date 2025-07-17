"""
ロギングサービスモジュール

このモジュールは、アプリケーション全体のログ操作を統一的に管理するための
LoggingServiceクラスを提供します。
"""

import time
import hashlib
from typing import Dict, Any, Optional, ContextManager
from contextlib import contextmanager
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.core.crud_config import LoggingConfig, PerformanceConfig


class LoggingService:
    """
    ログ操作を統一的に管理するサービスクラス
    
    このクラスは、構造化ログ、パフォーマンス監視、セキュリティ考慮を含む
    ログ機能を提供します。
    """
    
    def __init__(
        self,
        logging_config: LoggingConfig,
        performance_config: PerformanceConfig,
        logger_name: str = __name__
    ):
        """
        LoggingServiceを初期化する
        
        Args:
            logging_config: ログ設定
            performance_config: パフォーマンス設定
            logger_name: ロガー名（デフォルト: モジュール名）
        """
        self.logging_config = logging_config
        self.performance_config = performance_config
        self.logger = get_logger(logger_name)
        
    def log_operation(
        self,
        operation: str,
        status: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        構造化された操作ログを出力する
        
        Args:
            operation: 操作名（例: "user creation", "user update"）
            status: ステータス（"start", "success", "error"等）
            user_id: ユーザーID（自動的にハッシュ化される）
            **kwargs: 追加のログ情報
        """
        if not self._should_log_operation(operation):
            return
            
        log_data = {
            "operation": operation,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if user_id:
            log_data["user_id_hash"] = self.hash_identifier(str(user_id))
            
        # 追加のログデータをマージ
        log_data.update(kwargs)
        
        # ステータスに応じたログレベルの選択
        if status == "error":
            self.logger.error(
                f"Operation {operation} failed",
                extra=log_data
            )
        elif status == "start":
            self.logger.debug(
                f"Starting operation: {operation}",
                extra=log_data
            )
        else:  # success, その他
            self.logger.info(
                f"Operation {operation} completed with status: {status}",
                extra=log_data
            )
            
    def log_performance(
        self,
        operation: str,
        execution_time: float,
        query_type: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        パフォーマンスメトリクスをログに記録する
        
        Args:
            operation: 操作名
            execution_time: 実行時間（秒）
            query_type: クエリタイプ（"select", "insert"等）
            **kwargs: 追加のメトリクス情報
        """
        if not self.logging_config.log_performance_metrics:
            return
            
        log_data = {
            "operation": operation,
            "execution_time": execution_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if query_type:
            log_data["query_type"] = query_type
            
        # 追加のメトリクスデータをマージ
        log_data.update(kwargs)
        
        # スローログの検出
        if execution_time > self.performance_config.slow_query_threshold:
            self.logger.warning(
                f"Slow operation detected: {operation} took {execution_time:.3f}s",
                extra=log_data
            )
        elif execution_time > self.performance_config.performance_log_threshold:
            self.logger.info(
                f"Performance metrics for {operation}",
                extra=log_data
            )
        else:
            self.logger.debug(
                f"Performance metrics for {operation}",
                extra=log_data
            )
            
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        success: bool = True,
        **kwargs
    ) -> None:
        """
        セキュリティ関連のイベントをログに記録する
        
        Args:
            event_type: イベントタイプ（"authentication", "password_change"等）
            user_id: ユーザーID（自動的にハッシュ化される）
            success: 成功/失敗フラグ
            **kwargs: 追加のセキュリティ情報
        """
        if not self.logging_config.log_security_events:
            return
            
        log_data = {
            "event_type": event_type,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if user_id:
            log_data["user_id_hash"] = self.hash_identifier(str(user_id))
            
        # 追加のセキュリティデータをマージ（機密情報はフィルタリング）
        filtered_kwargs = self._filter_sensitive_data(kwargs)
        log_data.update(filtered_kwargs)
        
        # 成功/失敗に応じたログレベル
        if success:
            self.logger.info(
                f"Security event: {event_type}",
                extra=log_data
            )
        else:
            self.logger.warning(
                f"Security event failed: {event_type}",
                extra=log_data
            )
            
    @contextmanager
    def monitor_performance(
        self,
        operation: str,
        query_type: Optional[str] = None,
        **kwargs
    ) -> ContextManager[Dict[str, Any]]:
        """
        パフォーマンスを監視するコンテキストマネージャー
        
        Args:
            operation: 操作名
            query_type: クエリタイプ
            **kwargs: 追加のコンテキスト情報
            
        Yields:
            パフォーマンスデータを格納する辞書
        """
        start_time = time.time()
        context: Dict[str, Any] = {"operation": operation}
        
        if query_type:
            context["query_type"] = query_type
            
        try:
            yield context
        finally:
            execution_time = time.time() - start_time
            context["execution_time"] = execution_time
            
            # パフォーマンスログを出力
            self.log_performance(
                operation=operation,
                execution_time=execution_time,
                query_type=query_type,
                **kwargs
            )
            
    def hash_identifier(self, identifier: str) -> str:
        """
        識別子（ユーザーID等）をハッシュ化する
        
        Args:
            identifier: ハッシュ化する識別子
            
        Returns:
            ハッシュ化された識別子（最初の8文字）
        """
        return hashlib.sha256(identifier.encode()).hexdigest()[:8]
        
    def _should_log_operation(self, operation: str) -> bool:
        """
        操作ログを出力すべきかどうかを判定する
        
        Args:
            operation: 操作名
            
        Returns:
            ログを出力すべきかどうか
        """
        if not self.logging_config.log_user_operations:
            return False
            
        # セキュリティ関連の操作は常にログ
        security_operations = [
            "authentication", "password_change", "password_update",
            "user_deletion", "permission_change"
        ]
        
        if any(sec_op in operation.lower() for sec_op in security_operations):
            return self.logging_config.log_security_events
            
        return True
        
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        機密情報をフィルタリングする
        
        Args:
            data: フィルタリングするデータ
            
        Returns:
            フィルタリングされたデータ
        """
        sensitive_keys = [
            "password", "token", "secret", "key", "credential",
            "auth", "private", "passphrase"
        ]
        
        filtered_data = {}
        for key, value in data.items():
            # キー名に機密情報を示す単語が含まれる場合はスキップ
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered_data[key] = "[REDACTED]"
            else:
                filtered_data[key] = value
                
        return filtered_data


# デフォルトインスタンス（後方互換性のため）
from app.core.crud_config import DEFAULT_LOGGING_CONFIG, DEFAULT_PERFORMANCE_CONFIG

default_logging_service = LoggingService(
    logging_config=DEFAULT_LOGGING_CONFIG,
    performance_config=DEFAULT_PERFORMANCE_CONFIG
)