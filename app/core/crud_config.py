"""CRUD operations configuration module.

This module provides configuration classes for CRUD operations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CRUDConfig:
    """Configuration for CRUD operations.
    
    This class contains all configurable parameters for CRUD operations,
    including security settings, performance thresholds, and logging options.
    """
    
    # Security settings
    timing_attack_min_delay: float = 0.05  # 50ms minimum delay for timing attack prevention
    password_verification_min_delay: float = 0.25  # 250ms minimum delay for password verification
    user_id_hash_length: int = 8  # Length of hashed user ID for logging
    
    # Performance settings
    slow_query_threshold: float = 0.5  # 500ms threshold for slow query warnings
    performance_log_threshold: float = 0.1  # 100ms threshold for performance logging
    
    # Logging settings
    log_user_operations: bool = True  # Enable operation logging
    log_performance_metrics: bool = True  # Enable performance metrics logging
    log_security_events: bool = True  # Enable security event logging
    
    def __post_init__(self):
        """Validate configuration values after initialization."""
        if self.timing_attack_min_delay < 0:
            raise ValueError("timing_attack_min_delay must be non-negative")
        
        if self.password_verification_min_delay < 0:
            raise ValueError("password_verification_min_delay must be non-negative")
        
        if self.user_id_hash_length < 1:
            raise ValueError("user_id_hash_length must be positive")
        
        if self.slow_query_threshold < 0:
            raise ValueError("slow_query_threshold must be non-negative")
        
        if self.performance_log_threshold < 0:
            raise ValueError("performance_log_threshold must be non-negative")


@dataclass
class SecurityConfig:
    """Security-specific configuration.
    
    This class contains security-related configuration parameters.
    """
    
    timing_attack_min_delay: float = 0.05
    password_verification_min_delay: float = 0.25
    user_id_hash_length: int = 8
    log_security_events: bool = True
    
    def __post_init__(self):
        """Validate security configuration values."""
        if self.timing_attack_min_delay < 0:
            raise ValueError("timing_attack_min_delay must be non-negative")
        
        if self.password_verification_min_delay < 0:
            raise ValueError("password_verification_min_delay must be non-negative")
        
        if self.user_id_hash_length < 1:
            raise ValueError("user_id_hash_length must be positive")


@dataclass
class PerformanceConfig:
    """Performance monitoring configuration.
    
    This class contains performance monitoring related parameters.
    """
    
    slow_query_threshold: float = 0.5
    performance_log_threshold: float = 0.1
    log_performance_metrics: bool = True
    
    def __post_init__(self):
        """Validate performance configuration values."""
        if self.slow_query_threshold < 0:
            raise ValueError("slow_query_threshold must be non-negative")
        
        if self.performance_log_threshold < 0:
            raise ValueError("performance_log_threshold must be non-negative")


@dataclass
class LoggingConfig:
    """Logging configuration.
    
    This class contains logging-related configuration parameters.
    """
    
    log_user_operations: bool = True
    log_performance_metrics: bool = True
    log_security_events: bool = True


# Default configuration instance
DEFAULT_CRUD_CONFIG = CRUDConfig()
DEFAULT_SECURITY_CONFIG = SecurityConfig()
DEFAULT_PERFORMANCE_CONFIG = PerformanceConfig()
DEFAULT_LOGGING_CONFIG = LoggingConfig()