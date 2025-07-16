"""Unit tests for CRUD configuration classes."""

import pytest
from dataclasses import dataclass
from app.core.crud_config import (
    CRUDConfig,
    SecurityConfig,
    PerformanceConfig,
    LoggingConfig,
    DEFAULT_CRUD_CONFIG,
    DEFAULT_SECURITY_CONFIG,
    DEFAULT_PERFORMANCE_CONFIG,
    DEFAULT_LOGGING_CONFIG,
)


class TestCRUDConfig:
    """Test cases for CRUDConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = CRUDConfig()
        
        # Security settings
        assert config.timing_attack_min_delay == 0.05
        assert config.password_verification_min_delay == 0.25
        assert config.user_id_hash_length == 8
        
        # Performance settings
        assert config.slow_query_threshold == 0.5
        assert config.performance_log_threshold == 0.1
        
        # Logging settings
        assert config.log_user_operations is True
        assert config.log_performance_metrics is True
        assert config.log_security_events is True
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = CRUDConfig(
            timing_attack_min_delay=0.1,
            password_verification_min_delay=0.5,
            user_id_hash_length=12,
            slow_query_threshold=1.0,
            performance_log_threshold=0.2,
            log_user_operations=False,
            log_performance_metrics=False,
            log_security_events=False
        )
        
        assert config.timing_attack_min_delay == 0.1
        assert config.password_verification_min_delay == 0.5
        assert config.user_id_hash_length == 12
        assert config.slow_query_threshold == 1.0
        assert config.performance_log_threshold == 0.2
        assert config.log_user_operations is False
        assert config.log_performance_metrics is False
        assert config.log_security_events is False
    
    def test_validation_timing_attack_min_delay_negative(self):
        """Test validation for negative timing_attack_min_delay."""
        with pytest.raises(ValueError, match="timing_attack_min_delay must be non-negative"):
            CRUDConfig(timing_attack_min_delay=-0.1)
    
    def test_validation_password_verification_min_delay_negative(self):
        """Test validation for negative password_verification_min_delay."""
        with pytest.raises(ValueError, match="password_verification_min_delay must be non-negative"):
            CRUDConfig(password_verification_min_delay=-0.1)
    
    def test_validation_user_id_hash_length_zero(self):
        """Test validation for zero user_id_hash_length."""
        with pytest.raises(ValueError, match="user_id_hash_length must be positive"):
            CRUDConfig(user_id_hash_length=0)
    
    def test_validation_user_id_hash_length_negative(self):
        """Test validation for negative user_id_hash_length."""
        with pytest.raises(ValueError, match="user_id_hash_length must be positive"):
            CRUDConfig(user_id_hash_length=-1)
    
    def test_validation_slow_query_threshold_negative(self):
        """Test validation for negative slow_query_threshold."""
        with pytest.raises(ValueError, match="slow_query_threshold must be non-negative"):
            CRUDConfig(slow_query_threshold=-0.1)
    
    def test_validation_performance_log_threshold_negative(self):
        """Test validation for negative performance_log_threshold."""
        with pytest.raises(ValueError, match="performance_log_threshold must be non-negative"):
            CRUDConfig(performance_log_threshold=-0.1)
    
    def test_validation_zero_values_allowed(self):
        """Test that zero values are allowed for appropriate fields."""
        # These should not raise errors
        config = CRUDConfig(
            timing_attack_min_delay=0.0,
            password_verification_min_delay=0.0,
            slow_query_threshold=0.0,
            performance_log_threshold=0.0,
            user_id_hash_length=1  # Minimum positive value
        )
        
        assert config.timing_attack_min_delay == 0.0
        assert config.password_verification_min_delay == 0.0
        assert config.slow_query_threshold == 0.0
        assert config.performance_log_threshold == 0.0
        assert config.user_id_hash_length == 1


class TestSecurityConfig:
    """Test cases for SecurityConfig class."""
    
    def test_default_values(self):
        """Test default security configuration values."""
        config = SecurityConfig()
        
        assert config.timing_attack_min_delay == 0.05
        assert config.password_verification_min_delay == 0.25
        assert config.user_id_hash_length == 8
        assert config.log_security_events is True
    
    def test_custom_values(self):
        """Test custom security configuration values."""
        config = SecurityConfig(
            timing_attack_min_delay=0.1,
            password_verification_min_delay=0.5,
            user_id_hash_length=16,
            log_security_events=False
        )
        
        assert config.timing_attack_min_delay == 0.1
        assert config.password_verification_min_delay == 0.5
        assert config.user_id_hash_length == 16
        assert config.log_security_events is False
    
    def test_validation_timing_attack_min_delay_negative(self):
        """Test validation for negative timing_attack_min_delay."""
        with pytest.raises(ValueError, match="timing_attack_min_delay must be non-negative"):
            SecurityConfig(timing_attack_min_delay=-0.1)
    
    def test_validation_password_verification_min_delay_negative(self):
        """Test validation for negative password_verification_min_delay."""
        with pytest.raises(ValueError, match="password_verification_min_delay must be non-negative"):
            SecurityConfig(password_verification_min_delay=-0.1)
    
    def test_validation_user_id_hash_length_zero(self):
        """Test validation for zero user_id_hash_length."""
        with pytest.raises(ValueError, match="user_id_hash_length must be positive"):
            SecurityConfig(user_id_hash_length=0)


class TestPerformanceConfig:
    """Test cases for PerformanceConfig class."""
    
    def test_default_values(self):
        """Test default performance configuration values."""
        config = PerformanceConfig()
        
        assert config.slow_query_threshold == 0.5
        assert config.performance_log_threshold == 0.1
        assert config.log_performance_metrics is True
    
    def test_custom_values(self):
        """Test custom performance configuration values."""
        config = PerformanceConfig(
            slow_query_threshold=1.0,
            performance_log_threshold=0.2,
            log_performance_metrics=False
        )
        
        assert config.slow_query_threshold == 1.0
        assert config.performance_log_threshold == 0.2
        assert config.log_performance_metrics is False
    
    def test_validation_slow_query_threshold_negative(self):
        """Test validation for negative slow_query_threshold."""
        with pytest.raises(ValueError, match="slow_query_threshold must be non-negative"):
            PerformanceConfig(slow_query_threshold=-0.1)
    
    def test_validation_performance_log_threshold_negative(self):
        """Test validation for negative performance_log_threshold."""
        with pytest.raises(ValueError, match="performance_log_threshold must be non-negative"):
            PerformanceConfig(performance_log_threshold=-0.1)


class TestLoggingConfig:
    """Test cases for LoggingConfig class."""
    
    def test_default_values(self):
        """Test default logging configuration values."""
        config = LoggingConfig()
        
        assert config.log_user_operations is True
        assert config.log_performance_metrics is True
        assert config.log_security_events is True
    
    def test_custom_values(self):
        """Test custom logging configuration values."""
        config = LoggingConfig(
            log_user_operations=False,
            log_performance_metrics=False,
            log_security_events=False
        )
        
        assert config.log_user_operations is False
        assert config.log_performance_metrics is False
        assert config.log_security_events is False


class TestDefaultInstances:
    """Test cases for default configuration instances."""
    
    def test_default_crud_config(self):
        """Test DEFAULT_CRUD_CONFIG instance."""
        assert isinstance(DEFAULT_CRUD_CONFIG, CRUDConfig)
        assert DEFAULT_CRUD_CONFIG.timing_attack_min_delay == 0.05
        assert DEFAULT_CRUD_CONFIG.password_verification_min_delay == 0.25
        assert DEFAULT_CRUD_CONFIG.user_id_hash_length == 8
        assert DEFAULT_CRUD_CONFIG.slow_query_threshold == 0.5
        assert DEFAULT_CRUD_CONFIG.performance_log_threshold == 0.1
        assert DEFAULT_CRUD_CONFIG.log_user_operations is True
        assert DEFAULT_CRUD_CONFIG.log_performance_metrics is True
        assert DEFAULT_CRUD_CONFIG.log_security_events is True
    
    def test_default_security_config(self):
        """Test DEFAULT_SECURITY_CONFIG instance."""
        assert isinstance(DEFAULT_SECURITY_CONFIG, SecurityConfig)
        assert DEFAULT_SECURITY_CONFIG.timing_attack_min_delay == 0.05
        assert DEFAULT_SECURITY_CONFIG.password_verification_min_delay == 0.25
        assert DEFAULT_SECURITY_CONFIG.user_id_hash_length == 8
        assert DEFAULT_SECURITY_CONFIG.log_security_events is True
    
    def test_default_performance_config(self):
        """Test DEFAULT_PERFORMANCE_CONFIG instance."""
        assert isinstance(DEFAULT_PERFORMANCE_CONFIG, PerformanceConfig)
        assert DEFAULT_PERFORMANCE_CONFIG.slow_query_threshold == 0.5
        assert DEFAULT_PERFORMANCE_CONFIG.performance_log_threshold == 0.1
        assert DEFAULT_PERFORMANCE_CONFIG.log_performance_metrics is True
    
    def test_default_logging_config(self):
        """Test DEFAULT_LOGGING_CONFIG instance."""
        assert isinstance(DEFAULT_LOGGING_CONFIG, LoggingConfig)
        assert DEFAULT_LOGGING_CONFIG.log_user_operations is True
        assert DEFAULT_LOGGING_CONFIG.log_performance_metrics is True
        assert DEFAULT_LOGGING_CONFIG.log_security_events is True


class TestConfigurationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_values(self):
        """Test very large configuration values."""
        config = CRUDConfig(
            timing_attack_min_delay=999999.0,
            password_verification_min_delay=999999.0,
            user_id_hash_length=999999,
            slow_query_threshold=999999.0,
            performance_log_threshold=999999.0
        )
        
        assert config.timing_attack_min_delay == 999999.0
        assert config.password_verification_min_delay == 999999.0
        assert config.user_id_hash_length == 999999
        assert config.slow_query_threshold == 999999.0
        assert config.performance_log_threshold == 999999.0
    
    def test_minimal_valid_values(self):
        """Test minimal valid configuration values."""
        config = CRUDConfig(
            timing_attack_min_delay=0.0,
            password_verification_min_delay=0.0,
            user_id_hash_length=1,
            slow_query_threshold=0.0,
            performance_log_threshold=0.0
        )
        
        assert config.timing_attack_min_delay == 0.0
        assert config.password_verification_min_delay == 0.0
        assert config.user_id_hash_length == 1
        assert config.slow_query_threshold == 0.0
        assert config.performance_log_threshold == 0.0
    
    def test_dataclass_immutability(self):
        """Test that configuration objects are properly created as dataclasses."""
        config = CRUDConfig()
        
        # Should be able to modify values (dataclass is mutable by default)
        config.timing_attack_min_delay = 0.1
        assert config.timing_attack_min_delay == 0.1
        
        # Should have proper dataclass attributes
        assert hasattr(config, '__dataclass_fields__')
        assert 'timing_attack_min_delay' in config.__dataclass_fields__
    
    def test_configuration_independence(self):
        """Test that different config instances are independent."""
        config1 = CRUDConfig(timing_attack_min_delay=0.1)
        config2 = CRUDConfig(timing_attack_min_delay=0.2)
        
        assert config1.timing_attack_min_delay == 0.1
        assert config2.timing_attack_min_delay == 0.2
        
        # Modifying one should not affect the other
        config1.timing_attack_min_delay = 0.3
        assert config1.timing_attack_min_delay == 0.3
        assert config2.timing_attack_min_delay == 0.2