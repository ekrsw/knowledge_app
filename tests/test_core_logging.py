"""Tests for core logging functionality."""

import pytest
import logging
import json
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime

from app.core.logging import (
    get_logger,
    get_request_logger,
    CustomJsonFormatter,
    RequestIdFilter,
)
from app.core.config import settings


class TestRequestIdFilter:
    """RequestIdFilterのテスト"""

    def test_filter_adds_request_id(self):
        """リクエストIDが追加されることをテスト"""
        filter_instance = RequestIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None
        )
        
        # フィルター適用前はrequest_id属性がない
        assert not hasattr(record, "request_id")
        
        # フィルター適用
        result = filter_instance.filter(record)
        
        # フィルターは常にTrueを返す
        assert result is True
        # request_id属性が追加される
        assert hasattr(record, "request_id")
        assert record.request_id == "no-request-id"

    def test_filter_preserves_existing_request_id(self):
        """既存のリクエストIDが保持されることをテスト"""
        filter_instance = RequestIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None
        )
        
        # 事前にrequest_idを設定
        record.request_id = "test-request-123"
        
        # フィルター適用
        result = filter_instance.filter(record)
        
        assert result is True
        assert record.request_id == "test-request-123"


class TestCustomJsonFormatter:
    """CustomJsonFormatterのテスト"""

    def test_format_basic_log_record(self):
        """基本的なログレコードのJSON形式化をテスト"""
        formatter = CustomJsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.request_id = "test-123"
        record.module = "test_module"
        record.funcName = "test_function"
        
        # JSON形式の出力を取得
        result = formatter.format(record)
        
        # JSONとしてパース可能であることを確認
        log_data = json.loads(result)
        
        # 必要なフィールドが含まれていることを確認
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42
        assert log_data["request_id"] == "test-123"
        assert "timestamp" in log_data

    def test_format_with_exception(self):
        """例外情報付きログレコードのテスト"""
        formatter = CustomJsonFormatter()
        
        try:
            raise ValueError("Test exception")
        except Exception:
            import sys
            exc_info = sys.exc_info()
            
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        record.request_id = "error-123"
        record.module = "test_module"
        record.funcName = "test_function"
        
        # JSON形式の出力を取得
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # 例外情報が含まれていることを確認
        assert "exception" in log_data
        assert "ValueError: Test exception" in log_data["exception"]


class TestGetLogger:
    """get_logger関数のテスト"""

    def test_get_logger_basic(self):
        """基本的なロガー取得をテスト"""
        logger_name = "test_logger_basic"
        logger = get_logger(logger_name)
        
        assert logger.name == logger_name
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) > 0  # ハンドラーが追加されている

    def test_get_logger_already_configured(self):
        """既に設定済みロガーの場合のテスト"""
        logger_name = "test_logger_configured"
        
        # 1回目の呼び出し
        logger1 = get_logger(logger_name)
        handler_count1 = len(logger1.handlers)
        
        # 2回目の呼び出し（既に設定済み）
        logger2 = get_logger(logger_name)
        handler_count2 = len(logger2.handlers)
        
        # 同じロガーインスタンスが返され、ハンドラーが重複追加されない
        assert logger1 is logger2
        assert handler_count1 == handler_count2

    @patch('app.core.logging.settings')
    def test_get_logger_production_environment(self, mock_settings):
        """本番環境設定でのロガーテスト"""
        # 本番環境の設定をモック
        mock_settings.ENVIRONMENT = "production"
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.LOG_TO_FILE = False
        
        logger_name = "test_logger_production"
        logger = get_logger(logger_name)
        
        # JSONフォーマッターが使用されていることを確認
        console_handler = logger.handlers[0]
        assert isinstance(console_handler.formatter, CustomJsonFormatter)

    @patch('app.core.logging.settings')
    def test_get_logger_with_file_logging(self, mock_settings):
        """ファイルログ有効時のテスト"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                # ファイルログ有効の設定をモック
                mock_settings.ENVIRONMENT = "development"
                mock_settings.LOG_LEVEL = "DEBUG"
                mock_settings.LOG_TO_FILE = True
                mock_settings.LOG_FILE_PATH = tmp_file.name
                
                logger_name = "test_logger_file"
                logger = get_logger(logger_name)
                
                # コンソールハンドラーとファイルハンドラーの両方が存在
                assert len(logger.handlers) == 2
                
                # ファイルハンドラーが追加されていることを確認
                handler_types = [type(h).__name__ for h in logger.handlers]
                assert "StreamHandler" in handler_types
                assert "RotatingFileHandler" in handler_types
                
            finally:
                # 一時ファイルをクリーンアップ
                os.unlink(tmp_file.name)


class TestGetRequestLogger:
    """get_request_logger関数のテスト"""

    def test_get_request_logger_basic(self):
        """基本的なリクエストロガー取得をテスト"""
        # FastAPIのRequestオブジェクトをモック
        mock_request = Mock()
        mock_request.state = Mock()
        mock_request.state.request_id = "request-123"
        
        logger_adapter = get_request_logger(mock_request)
        
        assert isinstance(logger_adapter, logging.LoggerAdapter)
        assert logger_adapter.extra["request_id"] == "request-123"

    def test_get_request_logger_no_request_id(self):
        """リクエストIDがない場合のテスト"""
        # リクエストIDが設定されていないリクエストをモック
        mock_request = Mock()
        mock_request.state = Mock()
        # request_id属性がない状態をシミュレート
        del mock_request.state.request_id
        
        logger_adapter = get_request_logger(mock_request)
        
        assert isinstance(logger_adapter, logging.LoggerAdapter)
        assert logger_adapter.extra["request_id"] == "no-request-id"

    def test_get_request_logger_propagation_disabled(self):
        """ロガーの伝播が無効化されることをテスト"""
        mock_request = Mock()
        mock_request.state = Mock()
        mock_request.state.request_id = "propagation-test"
        
        logger_adapter = get_request_logger(mock_request)
        
        # 親ロガーへの伝播が無効化されていることを確認
        assert logger_adapter.logger.propagate is False


class TestLoggingIntegration:
    """ロギング機能の統合テスト"""

    def test_logging_with_request_id_filter(self):
        """リクエストIDフィルターを含むロギングの統合テスト"""
        logger_name = "test_integration"
        logger = get_logger(logger_name)
        
        # ログメッセージが正常に処理されることを確認
        logger.info("Test message")
        
        # ロガーにリクエストIDフィルターが追加されていることを確認
        has_request_id_filter = any(
            isinstance(f, RequestIdFilter) for f in logger.filters
        )
        assert has_request_id_filter

    def test_app_logger_exists(self):
        """アプリケーションロガーが存在することをテスト"""
        from app.core.logging import app_logger
        
        assert isinstance(app_logger, logging.Logger)
        assert app_logger.name == "app"