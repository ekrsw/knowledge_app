"""Tests for LoggingService functionality."""

import pytest
import time
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from contextlib import contextmanager

from app.core.logging_service import LoggingService
from app.core.crud_config import LoggingConfig, PerformanceConfig


class TestLoggingService:
    """LoggingServiceのテスト"""

    def test_init_with_default_config(self):
        """デフォルト設定でのインスタンス化テスト"""
        logging_config = LoggingConfig()
        performance_config = PerformanceConfig()
        
        service = LoggingService(logging_config, performance_config)
        
        assert service.logging_config == logging_config
        assert service.performance_config == performance_config
        assert service.logger.name == "app.core.logging_service"

    def test_init_with_custom_logger_name(self):
        """カスタムロガー名でのインスタンス化テスト"""
        logging_config = LoggingConfig()
        performance_config = PerformanceConfig()
        logger_name = "custom.logger.name"
        
        service = LoggingService(logging_config, performance_config, logger_name)
        
        assert service.logger.name == logger_name


class TestLogOperation:
    """log_operationメソッドのテスト"""

    def setup_method(self):
        """テスト前の設定"""
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.service = LoggingService(self.logging_config, self.performance_config)

    def test_log_operation_basic(self):
        """基本的な操作ログのテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_operation("user_creation", "success")
            
            # infoレベルでログが出力されることを確認
            mock_logger.info.assert_called_once()
            args, kwargs = mock_logger.info.call_args
            
            assert "user_creation" in args[0]
            assert "success" in args[0]
            assert "extra" in kwargs
            assert kwargs["extra"]["operation"] == "user_creation"
            assert kwargs["extra"]["status"] == "success"

    def test_log_operation_with_user_id(self):
        """ユーザーID付き操作ログのテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            user_id = "test-user-123"
            self.service.log_operation("user_update", "start", user_id=user_id)
            
            # debugレベルでログが出力されることを確認
            mock_logger.debug.assert_called_once()
            args, kwargs = mock_logger.debug.call_args
            
            assert "extra" in kwargs
            assert kwargs["extra"]["user_id_hash"] == self.service.hash_identifier(user_id)

    def test_log_operation_error_status(self):
        """エラーステータスの操作ログのテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_operation("user_deletion", "error")
            
            # errorレベルでログが出力されることを確認
            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            
            assert "failed" in args[0]
            assert kwargs["extra"]["status"] == "error"

    def test_log_operation_with_kwargs(self):
        """追加パラメータ付き操作ログのテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            extra_data = {"request_id": "req-123", "source": "api"}
            self.service.log_operation("password_change", "success", **extra_data)
            
            mock_logger.info.assert_called_once()
            args, kwargs = mock_logger.info.call_args
            
            assert kwargs["extra"]["request_id"] == "req-123"
            assert kwargs["extra"]["source"] == "api"

    def test_log_operation_disabled(self):
        """ログ機能が無効化されている場合のテスト"""
        # ログ機能を無効化
        self.logging_config.log_user_operations = False
        
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_operation("user_creation", "success")
            
            # ログが出力されないことを確認
            mock_logger.info.assert_not_called()
            mock_logger.debug.assert_not_called()
            mock_logger.error.assert_not_called()


class TestLogPerformance:
    """log_performanceメソッドのテスト"""

    def setup_method(self):
        """テスト前の設定"""
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.service = LoggingService(self.logging_config, self.performance_config)

    def test_log_performance_normal_execution(self):
        """通常の実行時間のパフォーマンスログテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            execution_time = 0.01  # 10ms（通常の実行時間）
            
            self.service.log_performance("get_user", execution_time)
            
            # debugレベルでログが出力されることを確認
            mock_logger.debug.assert_called_once()
            args, kwargs = mock_logger.debug.call_args
            
            assert kwargs["extra"]["execution_time"] == execution_time

    def test_log_performance_slow_query(self):
        """スロークエリのパフォーマンスログテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            execution_time = 2.0  # 2秒（スロークエリ）
            
            self.service.log_performance("complex_query", execution_time)
            
            # warningレベルでログが出力されることを確認
            mock_logger.warning.assert_called_once()
            args, kwargs = mock_logger.warning.call_args
            
            assert "Slow operation detected" in args[0]
            assert kwargs["extra"]["execution_time"] == execution_time

    def test_log_performance_with_query_type(self):
        """クエリタイプ付きパフォーマンスログテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            execution_time = 0.5  # 500ms（パフォーマンス閾値を超える）
            
            self.service.log_performance("get_users", execution_time, query_type="select")
            
            # infoレベルでログが出力されることを確認
            mock_logger.info.assert_called_once()
            args, kwargs = mock_logger.info.call_args
            
            assert kwargs["extra"]["query_type"] == "select"

    def test_log_performance_disabled(self):
        """パフォーマンス監視が無効化されている場合のテスト"""
        # パフォーマンス監視を無効化
        self.logging_config.log_performance_metrics = False
        
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_performance("test_operation", 1.0)
            
            # ログが出力されないことを確認
            mock_logger.debug.assert_not_called()
            mock_logger.info.assert_not_called()
            mock_logger.warning.assert_not_called()


class TestLogSecurityEvent:
    """log_security_eventメソッドのテスト"""

    def setup_method(self):
        """テスト前の設定"""
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.service = LoggingService(self.logging_config, self.performance_config)

    def test_log_security_event_success(self):
        """セキュリティイベント成功のログテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            user_id = "user-123"
            
            self.service.log_security_event("authentication", user_id=user_id, success=True)
            
            # infoレベルでログが出力されることを確認
            mock_logger.info.assert_called_once()
            args, kwargs = mock_logger.info.call_args
            
            assert "authentication" in args[0]
            assert kwargs["extra"]["success"] is True
            assert kwargs["extra"]["user_id_hash"] == self.service.hash_identifier(user_id)

    def test_log_security_event_failure(self):
        """セキュリティイベント失敗のログテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_security_event("password_change", success=False)
            
            # warningレベルでログが出力されることを確認
            mock_logger.warning.assert_called_once()
            args, kwargs = mock_logger.warning.call_args
            
            assert "failed" in args[0]
            assert kwargs["extra"]["success"] is False

    def test_log_security_event_with_sensitive_data(self):
        """機密データを含むセキュリティイベントのログテスト"""
        with patch.object(self.service, 'logger') as mock_logger:
            sensitive_data = {
                "password": "secret123",
                "token": "abc123",
                "username": "testuser"
            }
            
            self.service.log_security_event("login_attempt", **sensitive_data)
            
            mock_logger.info.assert_called_once()
            args, kwargs = mock_logger.info.call_args
            
            # 機密データがフィルタリングされていることを確認
            assert kwargs["extra"]["password"] == "[REDACTED]"
            assert kwargs["extra"]["token"] == "[REDACTED]"
            assert kwargs["extra"]["username"] == "testuser"  # 機密データではない

    def test_log_security_event_disabled(self):
        """セキュリティイベントログが無効化されている場合のテスト"""
        # セキュリティイベントログを無効化
        self.logging_config.log_security_events = False
        
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_security_event("authentication", success=True)
            
            # ログが出力されないことを確認
            mock_logger.info.assert_not_called()
            mock_logger.warning.assert_not_called()


class TestMonitorPerformance:
    """monitor_performanceコンテキストマネージャーのテスト"""

    def setup_method(self):
        """テスト前の設定"""
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.service = LoggingService(self.logging_config, self.performance_config)

    def test_monitor_performance_basic(self):
        """基本的なパフォーマンス監視のテスト"""
        with patch.object(self.service, 'log_performance') as mock_log_performance:
            with self.service.monitor_performance("test_operation") as context:
                # コンテキストが正しく設定されていることを確認
                assert context["operation"] == "test_operation"
                time.sleep(0.01)  # 少し待機
            
            # パフォーマンスログが呼び出されることを確認
            mock_log_performance.assert_called_once()
            args, kwargs = mock_log_performance.call_args
            
            assert kwargs["operation"] == "test_operation"
            assert kwargs["execution_time"] > 0

    def test_monitor_performance_with_query_type(self):
        """クエリタイプ付きパフォーマンス監視のテスト"""
        with patch.object(self.service, 'log_performance') as mock_log_performance:
            with self.service.monitor_performance("database_query", query_type="select") as context:
                assert context["query_type"] == "select"
            
            args, kwargs = mock_log_performance.call_args
            assert kwargs["query_type"] == "select"

    def test_monitor_performance_with_exception(self):
        """例外発生時のパフォーマンス監視のテスト"""
        with patch.object(self.service, 'log_performance') as mock_log_performance:
            with pytest.raises(ValueError):
                with self.service.monitor_performance("failing_operation"):
                    raise ValueError("Test exception")
            
            # 例外が発生してもパフォーマンスログは出力される
            mock_log_performance.assert_called_once()


class TestUtilityMethods:
    """ユーティリティメソッドのテスト"""

    def setup_method(self):
        """テスト前の設定"""
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.service = LoggingService(self.logging_config, self.performance_config)

    def test_hash_identifier(self):
        """識別子ハッシュ化のテスト"""
        identifier = "test-user-123"
        result = self.service.hash_identifier(identifier)
        
        # 8文字のハッシュが返されることを確認
        assert len(result) == 8
        assert isinstance(result, str)
        
        # 同じ識別子は同じハッシュを返す
        assert self.service.hash_identifier(identifier) == result

    def test_should_log_operation_user_operations_disabled(self):
        """ユーザー操作ログが無効化されている場合のテスト"""
        self.logging_config.log_user_operations = False
        
        result = self.service._should_log_operation("user_creation")
        assert result is False

    def test_should_log_operation_security_operation(self):
        """セキュリティ操作のログ判定テスト"""
        security_operations = ["authentication", "password_change", "user_deletion"]
        
        for operation in security_operations:
            result = self.service._should_log_operation(operation)
            assert result == self.logging_config.log_security_events

    def test_should_log_operation_normal_operation(self):
        """通常操作のログ判定テスト"""
        result = self.service._should_log_operation("user_creation")
        assert result is True

    def test_filter_sensitive_data(self):
        """機密データフィルタリングのテスト"""
        sensitive_data = {
            "password": "secret123",
            "token": "abc123",
            "auth_key": "key123",
            "username": "testuser",
            "email": "test@example.com"
        }
        
        result = self.service._filter_sensitive_data(sensitive_data)
        
        # 機密データがフィルタリングされていることを確認
        assert result["password"] == "[REDACTED]"
        assert result["token"] == "[REDACTED]"
        assert result["auth_key"] == "[REDACTED]"
        
        # 非機密データは保持される
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"

    def test_filter_sensitive_data_empty(self):
        """空のデータのフィルタリングテスト"""
        result = self.service._filter_sensitive_data({})
        assert result == {}


class TestDefaultInstance:
    """デフォルトインスタンスのテスト"""

    def test_default_logging_service_exists(self):
        """デフォルトログサービスの存在確認"""
        from app.core.logging_service import default_logging_service
        
        assert isinstance(default_logging_service, LoggingService)
        assert hasattr(default_logging_service, 'log_operation')
        assert hasattr(default_logging_service, 'log_performance')
        assert hasattr(default_logging_service, 'log_security_event')
        assert hasattr(default_logging_service, 'monitor_performance')


class TestIntegration:
    """統合テスト"""

    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        logging_config = LoggingConfig()
        performance_config = PerformanceConfig()
        service = LoggingService(logging_config, performance_config)
        
        with patch.object(service, 'logger') as mock_logger:
            # 操作開始
            service.log_operation("user_creation", "start", user_id="user-123")
            
            # パフォーマンス監視
            with service.monitor_performance("database_operation"):
                time.sleep(0.01)
            
            # セキュリティイベント
            service.log_security_event("user_created", user_id="user-123", success=True)
            
            # 操作完了
            service.log_operation("user_creation", "success", user_id="user-123")
            
            # 複数のログが出力されることを確認
            assert mock_logger.debug.call_count >= 1
            assert mock_logger.info.call_count >= 1