"""Unit tests for SecurityService."""

import pytest
import time
from unittest.mock import patch, MagicMock
from uuid import UUID, uuid4

from app.core.security_service import SecurityService, DEFAULT_SECURITY_SERVICE
from app.core.crud_config import SecurityConfig


class TestSecurityService:
    """Test cases for SecurityService class."""
    
    def test_default_initialization(self):
        """Test SecurityService initialization with default config."""
        service = SecurityService()
        
        assert service.config is not None
        assert service.config.timing_attack_min_delay == 0.05
        assert service.config.password_verification_min_delay == 0.25
        assert service.config.user_id_hash_length == 8
        assert service.config.log_security_events is True
        assert service.pwd_context is not None
    
    def test_custom_config_initialization(self):
        """Test SecurityService initialization with custom config."""
        config = SecurityConfig(
            timing_attack_min_delay=0.1,
            password_verification_min_delay=0.5,
            user_id_hash_length=16,
            log_security_events=False
        )
        
        service = SecurityService(config)
        
        assert service.config == config
        assert service.config.timing_attack_min_delay == 0.1
        assert service.config.password_verification_min_delay == 0.5
        assert service.config.user_id_hash_length == 16
        assert service.config.log_security_events is False
    
    def test_hash_password(self):
        """Test password hashing."""
        service = SecurityService()
        password = "test_password_123"
        
        hashed = service.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
        # bcrypt hashes typically start with $2b$
        assert hashed.startswith("$2b$")
    
    def test_hash_password_different_results(self):
        """Test that same password produces different hashes (due to salt)."""
        service = SecurityService()
        password = "test_password_123"
        
        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)
        
        assert hash1 != hash2
        assert len(hash1) == len(hash2)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        service = SecurityService()
        password = "test_password_123"
        
        hashed = service.hash_password(password)
        result = service.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        service = SecurityService()
        password = "test_password_123"
        wrong_password = "wrong_password"
        
        hashed = service.hash_password(password)
        result = service.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_hash_user_id(self):
        """Test user ID hashing."""
        service = SecurityService()
        user_id = uuid4()
        
        hashed = service.hash_user_id(user_id)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) == 8  # Default hash length
        assert hashed != str(user_id)
    
    def test_hash_user_id_consistent(self):
        """Test that same user ID produces same hash."""
        service = SecurityService()
        user_id = uuid4()
        
        hash1 = service.hash_user_id(user_id)
        hash2 = service.hash_user_id(user_id)
        
        assert hash1 == hash2
    
    def test_hash_user_id_different_ids(self):
        """Test that different user IDs produce different hashes."""
        service = SecurityService()
        user_id1 = uuid4()
        user_id2 = uuid4()
        
        hash1 = service.hash_user_id(user_id1)
        hash2 = service.hash_user_id(user_id2)
        
        assert hash1 != hash2
    
    def test_hash_user_id_custom_length(self):
        """Test user ID hashing with custom length."""
        config = SecurityConfig(user_id_hash_length=16)
        service = SecurityService(config)
        user_id = uuid4()
        
        hashed = service.hash_user_id(user_id)
        
        assert len(hashed) == 16
    
    def test_constant_time_operation(self):
        """Test constant time operation."""
        service = SecurityService()
        min_delay = 0.1
        
        start_time = time.time()
        service.constant_time_operation(min_delay)
        elapsed = time.time() - start_time
        
        # Should take at least min_delay time
        assert elapsed >= min_delay
        # Should not take significantly more than min_delay
        assert elapsed < min_delay + 0.05
    
    def test_verify_password_with_timing_protection(self):
        """Test password verification with timing protection."""
        service = SecurityService()
        password = "test_password_123"
        hashed = service.hash_password(password)
        
        # Test correct password
        start_time = time.time()
        result = service.verify_password_with_timing_protection(password, hashed)
        elapsed = time.time() - start_time
        
        assert result is True
        assert elapsed >= 0.25  # Should take at least min_delay
    
    def test_verify_password_with_timing_protection_incorrect(self):
        """Test password verification with timing protection for incorrect password."""
        service = SecurityService()
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = service.hash_password(password)
        
        # Test incorrect password
        start_time = time.time()
        result = service.verify_password_with_timing_protection(wrong_password, hashed)
        elapsed = time.time() - start_time
        
        assert result is False
        assert elapsed >= 0.25  # Should take at least min_delay
    
    @patch('app.core.security_service.logger')
    def test_verify_password_with_timing_protection_logging(self, mock_logger):
        """Test password verification with timing protection logging."""
        service = SecurityService()
        password = "test_password_123"
        hashed = service.hash_password(password)
        
        service.verify_password_with_timing_protection(password, hashed)
        
        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args
        assert call_args[0][0] == "Password verification completed"
        assert "operation" in call_args[1]["extra"]
        assert "execution_time" in call_args[1]["extra"]
        assert "result" in call_args[1]["extra"]
    
    @patch('app.core.security_service.logger')
    def test_verify_password_with_timing_protection_no_logging(self, mock_logger):
        """Test password verification with timing protection when logging is disabled."""
        config = SecurityConfig(log_security_events=False)
        service = SecurityService(config)
        password = "test_password_123"
        hashed = service.hash_password(password)
        
        service.verify_password_with_timing_protection(password, hashed)
        
        mock_logger.debug.assert_not_called()
    
    def test_apply_timing_attack_protection(self):
        """Test apply timing attack protection."""
        service = SecurityService()
        min_delay = 0.1
        
        start_time = time.time()
        service.apply_timing_attack_protection(start_time, min_delay)
        elapsed = time.time() - start_time
        
        assert elapsed >= min_delay
    
    def test_apply_timing_attack_protection_default_delay(self):
        """Test apply timing attack protection with default delay."""
        service = SecurityService()
        
        start_time = time.time()
        service.apply_timing_attack_protection(start_time)
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.05  # Default timing_attack_min_delay
    
    @patch('app.core.security_service.logger')
    def test_apply_timing_attack_protection_logging(self, mock_logger):
        """Test apply timing attack protection logging."""
        service = SecurityService()
        min_delay = 0.1
        
        start_time = time.time()
        service.apply_timing_attack_protection(start_time, min_delay)
        
        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args
        assert call_args[0][0] == "Timing attack protection applied"
        assert "operation" in call_args[1]["extra"]
        assert "total_execution_time" in call_args[1]["extra"]
        assert "min_delay" in call_args[1]["extra"]
        assert "protection_applied" in call_args[1]["extra"]
    
    @patch('app.core.security_service.logger')
    def test_apply_timing_attack_protection_no_logging(self, mock_logger):
        """Test apply timing attack protection when logging is disabled."""
        config = SecurityConfig(log_security_events=False)
        service = SecurityService(config)
        min_delay = 0.1
        
        start_time = time.time()
        service.apply_timing_attack_protection(start_time, min_delay)
        
        mock_logger.debug.assert_not_called()


class TestDefaultSecurityService:
    """Test cases for default SecurityService instance."""
    
    def test_default_instance(self):
        """Test default SecurityService instance."""
        assert DEFAULT_SECURITY_SERVICE is not None
        assert isinstance(DEFAULT_SECURITY_SERVICE, SecurityService)
        assert DEFAULT_SECURITY_SERVICE.config is not None
    
    def test_default_instance_functionality(self):
        """Test default SecurityService instance functionality."""
        password = "test_password_123"
        user_id = uuid4()
        
        # Test password operations
        hashed = DEFAULT_SECURITY_SERVICE.hash_password(password)
        assert DEFAULT_SECURITY_SERVICE.verify_password(password, hashed) is True
        
        # Test user ID hashing
        hashed_id = DEFAULT_SECURITY_SERVICE.hash_user_id(user_id)
        assert len(hashed_id) == 8


class TestSecurityServiceEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_password(self):
        """Test hashing and verification with empty password."""
        service = SecurityService()
        password = ""
        
        hashed = service.hash_password(password)
        assert service.verify_password(password, hashed) is True
        assert service.verify_password("not_empty", hashed) is False
    
    def test_very_long_password(self):
        """Test hashing and verification with very long password."""
        service = SecurityService()
        password = "a" * 1000
        
        hashed = service.hash_password(password)
        assert service.verify_password(password, hashed) is True
    
    def test_special_characters_password(self):
        """Test hashing and verification with special characters."""
        service = SecurityService()
        password = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        hashed = service.hash_password(password)
        assert service.verify_password(password, hashed) is True
    
    def test_unicode_password(self):
        """Test hashing and verification with unicode characters."""
        service = SecurityService()
        password = "テストパスワード123"
        
        hashed = service.hash_password(password)
        assert service.verify_password(password, hashed) is True
    
    def test_zero_hash_length(self):
        """Test user ID hashing with zero length should raise error."""
        with pytest.raises(ValueError, match="user_id_hash_length must be positive"):
            SecurityConfig(user_id_hash_length=0)
    
    def test_negative_timing_delays(self):
        """Test negative timing delays should raise error."""
        with pytest.raises(ValueError, match="timing_attack_min_delay must be non-negative"):
            SecurityConfig(timing_attack_min_delay=-0.1)
        
        with pytest.raises(ValueError, match="password_verification_min_delay must be non-negative"):
            SecurityConfig(password_verification_min_delay=-0.1)
    
    def test_very_small_timing_delays(self):
        """Test very small timing delays."""
        config = SecurityConfig(
            timing_attack_min_delay=0.001,
            password_verification_min_delay=0.001
        )
        service = SecurityService(config)
        
        start_time = time.time()
        service.apply_timing_attack_protection(start_time, 0.001)
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.001
    
    def test_very_large_timing_delays(self):
        """Test very large timing delays (should work but be slow)."""
        config = SecurityConfig(
            timing_attack_min_delay=0.1,
            password_verification_min_delay=0.1
        )
        service = SecurityService(config)
        
        start_time = time.time()
        service.apply_timing_attack_protection(start_time, 0.1)
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.1
        assert elapsed < 0.2  # Should not take much longer than required