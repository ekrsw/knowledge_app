"""Security service for CRUD operations.

This module provides security-related functionality including password hashing,
user ID hashing, and timing attack protection.
"""

import hashlib
import time
from typing import Optional
from uuid import UUID

from passlib.context import CryptContext

from app.core.crud_config import SecurityConfig, DEFAULT_SECURITY_CONFIG
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityService:
    """Security service for CRUD operations.
    
    This class provides security-related functionality including:
    - Password hashing and verification
    - User ID hashing for secure logging
    - Timing attack protection
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize security service with configuration.
        
        Args:
            config: Security configuration. If None, uses default configuration.
        """
        self.config = config or DEFAULT_SECURITY_CONFIG
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password is correct, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def hash_user_id(self, user_id: UUID) -> str:
        """Hash user ID for secure logging.
        
        Args:
            user_id: User ID to hash
            
        Returns:
            Hashed user ID string truncated to configured length
        """
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:self.config.user_id_hash_length]
    
    def constant_time_operation(self, min_delay: float) -> None:
        """Ensure a minimum execution time to prevent timing attacks.
        
        Args:
            min_delay: Minimum delay in seconds
        """
        start_time = time.time()
        elapsed = time.time() - start_time
        
        if elapsed < min_delay:
            remaining = min_delay - elapsed
            time.sleep(remaining)
    
    def verify_password_with_timing_protection(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password with timing attack protection.
        
        This method ensures a minimum execution time regardless of whether
        the password is correct or not, protecting against timing attacks.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password is correct, False otherwise
        """
        start_time = time.time()
        
        # Perform password verification
        is_valid = self.verify_password(plain_password, hashed_password)
        
        # Ensure minimum execution time
        min_time = self.config.password_verification_min_delay
        elapsed = time.time() - start_time
        
        if elapsed < min_time:
            remaining = min_time - elapsed
            time.sleep(remaining)
        
        if self.config.log_security_events:
            logger.debug(
                "Password verification completed",
                extra={
                    "operation": "verify_password_with_timing_protection",
                    "execution_time": time.time() - start_time,
                    "result": is_valid
                }
            )
        
        return is_valid
    
    def apply_timing_attack_protection(self, start_time: float, min_delay: Optional[float] = None) -> None:
        """Apply timing attack protection by ensuring minimum execution time.
        
        Args:
            start_time: The start time of the operation
            min_delay: Minimum delay in seconds. If None, uses config default.
        """
        if min_delay is None:
            min_delay = self.config.timing_attack_min_delay
        
        elapsed = time.time() - start_time
        
        if elapsed < min_delay:
            remaining = min_delay - elapsed
            time.sleep(remaining)
        
        if self.config.log_security_events:
            total_time = time.time() - start_time
            logger.debug(
                "Timing attack protection applied",
                extra={
                    "operation": "apply_timing_attack_protection",
                    "total_execution_time": total_time,
                    "min_delay": min_delay,
                    "protection_applied": elapsed < min_delay
                }
            )


# Default security service instance
DEFAULT_SECURITY_SERVICE = SecurityService()