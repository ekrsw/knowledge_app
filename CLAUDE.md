# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **knowledge_app** - a Python-based web application built with **FastAPI** and **PostgreSQL**. It's designed as a user management system with authentication capabilities, implemented with modern async patterns, comprehensive error handling, and a clean, service-oriented architecture.

## Technology Stack

- **FastAPI** - Web framework for building APIs
- **PostgreSQL** - Database with async support via asyncpg
- **SQLAlchemy 2.0** - Modern ORM with async capabilities
- **Alembic** - Database migrations
- **Pydantic** - Data validation and settings management
- **passlib + bcrypt** - Password hashing
- **greenlet** - Required for SQLAlchemy async operations

## Development Setup

### Environment Configuration
1. Copy `.env.example` to `.env` and configure database settings:
   ```
   USER_POSTGRES_HOST=localhost
   USER_POSTGRES_PORT=5432
   USER_POSTGRES_USER=my_user
   USER_POSTGRES_PASSWORD=password
   USER_POSTGRES_DB=my_database
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Operations

#### Verify Database Tables
```bash
python check_tables.py
```

#### Running Migrations
```bash
alembic upgrade head
```

#### Creating New Migrations
```bash
alembic revision --autogenerate -m "Description of changes"
alembic downgrade -1              # Rollback to previous migration
alembic history                   # Show migration history
alembic current                   # Show current migration
```

#### Running the Application
```bash
python -m app.main    # Run as module (recommended)
```
Note: Currently runs as a demo script, not as an API server.

### Testing

#### Comprehensive Test Suite
The application features an extensive test suite with **216 test methods** across **21 test files**, achieving high test coverage:

**Test Categories:**
- **Core Tests**:
  - `test_core_exceptions.py` - Core exception handling
  - `test_core_logging.py` - Logging functionality
  - `test_crud_config.py` - Configuration classes (28 tests)
  - `test_security_service.py` - Security service functionality (29 tests)
  - `test_crud_exceptions.py` - CRUD exception handling

- **CRUD User Tests**:
  - `test_crud_user_basic.py` - Core CRUD functionality
  - `test_crud_user_error_handling.py` - Exception handling
  - `test_crud_user_validation.py` - Input validation and constraints
  - `test_crud_user_security.py` - Password hashing, authentication, timing attacks
  - `test_crud_user_security_enhanced.py` - Advanced security features
  - `test_crud_user_optional_fields.py` - Field combinations and permissions
  - `test_crud_user_edge_cases.py` - Boundary values, memory limits, concurrency
  - `test_crud_user_transactions.py` - ACID properties, rollback, isolation
  - `test_crud_user_integration.py` - Real-world workflows, admin operations
  - `test_crud_user_update.py` - User update functionality
  - `test_crud_user_update_password.py` - Password change operations
  - `test_crud_user_concurrency.py` - Race condition and concurrent access tests
  - `test_crud_user_type_safety.py` - UUID type consistency tests
  - `test_crud_user_pagination.py` - Performance optimization and pagination tests
  - `test_crud_user_delete.py` - User deletion functionality

- **Performance Tests**:
  - `test_index_performance.py` - Database index optimization verification

#### Running Tests
```bash
pytest                          # Run all tests (216 tests)
pytest -v                       # Verbose output
pytest --cov=app                # Run with coverage report
pytest --cov=app --cov-report=html  # Generate HTML coverage report
pytest tests/test_crud_user_security.py  # Run specific test file
pytest tests/test_security_service.py    # Run security service tests
pytest tests/test_crud_config.py         # Run configuration tests
pytest -k "test_create_user"    # Run tests matching pattern
pytest -x                       # Stop at first failure
pytest --tb=short               # Shorter traceback format
```

#### Test Configuration
- **pytest.ini** configures async mode, test discovery, and disabled concurrent execution with `-x` flag for stopping at first failure
- **conftest.py** provides three session fixtures:
  - `clean_db_session` - Cleans test data before/after (recommended for most tests)
  - `rollback_db_session` - Always rolls back changes (for tests that don't need persistence)
  - `simple_db_session` - Manual commit control (for advanced scenarios)
- Tests automatically clean up data with username patterns like 'test%', 'another%', etc.
- InterfaceError prevention: Concurrent execution disabled via `--dist=no` in pytest.ini

## Architecture

### Service-Oriented Architecture
The application follows a clean service-oriented architecture with dependency injection:

- **Models** (`app/models/`) - SQLAlchemy ORM models
- **Schemas** (`app/schemas/`) - Pydantic models for request/response validation
- **CRUD** (`app/crud/`) - Data access layer with async operations
- **Core Services** (`app/core/`) - Business logic services with clean separation:
  - `security_service.py` - Security operations (password hashing, timing attack protection)
  - `crud_config.py` - Configuration management with validation
  - `logging.py` - Structured logging utilities
  - `config.py` - Environment configuration
  - `exceptions.py` - Custom exception hierarchy
- **Database** (`app/db/`) - Session management and initialization

### Dependency Injection Pattern
The application uses constructor-based dependency injection:

```python
from app.core.security_service import SecurityService
from app.core.crud_config import CRUDConfig

# Configure services
config = CRUDConfig(timing_attack_min_delay=0.1)
security_service = SecurityService(config.security_config)
crud_user = CRUDUser(config=config, security_service=security_service)
```

### Async Pattern
- All database operations are async using SQLAlchemy 2.0
- Session management through `AsyncSessionLocal` with `expire_on_commit=False`
- Async context managers for database transactions
- Greenlet required for proper async operation
- **Critical**: Access object attributes immediately after database operations before session context ends
- **Session Pattern**: Use `async with AsyncSessionLocal() as session:` for proper cleanup

### Error Handling
- Custom exception hierarchy in `app/crud/exceptions.py`
- PostgreSQL-specific error code handling (23505 for duplicates, 23502 for NOT NULL violations)
- Pre-validation approach to avoid database-specific errors
- Comprehensive structured logging with operation tracking
- Rollback handling for failed transactions

## Key Components

### Configuration System
**External Configuration** (`app/core/crud_config.py`):
- `CRUDConfig` - Main configuration class with validation
- `SecurityConfig` - Security-specific settings (timing delays, hash lengths)
- `PerformanceConfig` - Performance monitoring thresholds
- `LoggingConfig` - Logging behavior control
- **Default instances** available for backward compatibility

### Security Service
**SecurityService** (`app/core/security_service.py`):
- `hash_password()` - Secure password hashing with bcrypt
- `verify_password_with_timing_protection()` - Timing attack resistant verification
- `hash_user_id()` - Secure user ID hashing for logging
- `apply_timing_attack_protection()` - Configurable timing attack prevention
- **Configurable** through SecurityConfig with sensible defaults

### User Management
The `CRUDUser` class in `app/crud/user.py` provides:
- `create_user()` - User creation with duplicate validation
- `get_user_by_id()` - Retrieve user by UUID
- `get_user_by_username()` - Retrieve user by username
- `get_user_by_email()` - Retrieve user by email
- `get_all_users()` - Retrieve all users with optional pagination
- `get_users_paginated()` - Retrieve users with pagination metadata
- `update_user_by_id()` - Update user information
- `update_password()` - Update user password with verification
- `delete_user_by_id()` - Delete user by ID (with backward compatibility alias `delete_user`)
- `get_active_users()` - Retrieve only active users (optimized with index)
- `get_users_by_group()` - Retrieve users by group (optimized with index)
- `get_recent_users()` - Retrieve recently created users (optimized with index)

### Pagination Support
Pagination functionality with performance optimization:
- `PaginationParams` schema (page, limit, offset calculation)
- `PaginatedUsers` response schema with metadata
- Performance monitoring for queries
- Backward compatibility maintained

### Database Models
User model (`app/models/user.py`) includes:
- UUID primary key
- Authentication fields (username, email, hashed_password)
- Profile information (full_name, ctstage_name, sweet_name)
- Organization data (group enum: CSC_1, CSC_2, CSC_N, HHD)
- Permission flags (is_active, is_admin, is_sv)
- Timezone-aware timestamps

### Database Optimization
**Strategic Indexes** for performance:
- `idx_users_is_active_true` - Partial index for active users
- `idx_users_group` - Group filtering optimization
- `idx_users_created_at_desc` - Recent users optimization
- `idx_users_active_created_desc` - Composite index for complex queries

## Development Patterns

### Creating New CRUD Operations
1. Define the operation in the appropriate CRUD class
2. Use dependency injection for services (SecurityService, etc.)
3. Use async session management with proper cleanup
4. Implement error handling using custom exceptions
5. Add comprehensive structured logging with operation context
6. Write tests covering all scenarios including edge cases

### Adding New Services
1. Create service class in `app/core/`
2. Define configuration class if needed
3. Implement dependency injection in constructor
4. Add comprehensive unit tests
5. Update CRUDUser or other classes to use the service
6. Ensure backward compatibility with default instances

### Database Schema Changes
1. Modify the model in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit the migration file if needed
4. Apply migration: `alembic upgrade head`
5. Update tests to cover new fields/constraints
6. Consider adding indexes for frequently queried fields

### Testing Best Practices
- Use `clean_db_session` fixture for most tests
- Store primitive values (not ORM objects) after commit
- Implement comprehensive cleanup to avoid test interference
- Follow naming convention: `test_<module>_<category>.py`
- Test both positive and negative scenarios
- Mock external dependencies when testing services

## Current State

### Application Status
The application currently serves as a **CRUD operations demonstration** with a sophisticated service-oriented architecture. The `app/main.py` file acts as both the entry point and test runner for user management operations.

### What's Implemented
- **Complete user management CRUD operations** with async patterns
- **Service-oriented architecture** with dependency injection
- **External configuration system** with validation
- **Dedicated security service** with timing attack protection
- **Pagination support** for scalable data retrieval
- **Comprehensive error handling** with custom exceptions
- **Database migrations** with Alembic
- **Performance-optimized database indexes**
- **Extensive test suite** with 216 tests
- **Structured logging** with operation tracking and performance monitoring
- **PostgreSQL-specific optimizations** and TOCTOU race condition fixes
- **Advanced security features** (timing attack resistance, information leak prevention)

### What's Missing
- FastAPI REST API endpoints and route handlers
- Authentication middleware (JWT tokens)
- API documentation (OpenAPI/Swagger)
- Production error handlers and middleware
- Code quality tools (linting, formatting, pre-commit hooks)
- API rate limiting and request validation
- Background task processing
- Production deployment configuration

## Security Considerations
- **Passwords hashed** using bcrypt with configurable cost factor (default: 12)
- **UUID primary keys** prevent enumeration attacks
- **Timing attack resistant** authentication operations with configurable delays
- **Environment-based configuration** for sensitive data
- **No plain text passwords** in logs or error messages
- **Input validation** at multiple layers (Pydantic + database constraints)
- **Secure logging** with hashed user IDs and structured format
- **Configurable security parameters** through SecurityConfig

## Documentation
- `docs/crud-user-refactoring-plan.md` - Comprehensive 3-phase refactoring plan (Phase 3.4.2 complete)
- `docs/index-optimization-analysis.md` - Database index optimization analysis and recommendations
- `docs/naming-conventions.md` - CRUD method naming standards and conventions
- `docs/logging-guidelines.md` - Comprehensive logging standards and best practices
- Detailed docstrings in CRUD operations and services
- Type hints throughout the codebase for better IDE support

## Recent Changes

### Phase 3.4.2 - Security Service Separation (2025-07-16)
- **SecurityService Architecture**: Separated security concerns into dedicated service
  - Password hashing and verification with timing protection
  - User ID hashing for secure logging
  - Configurable timing attack protection
  - Comprehensive security event logging
- **Dependency Injection**: Implemented constructor-based dependency injection
- **29 New Tests**: Added comprehensive SecurityService test suite
- **Full Integration**: All 216 tests pass with zero regressions

### Phase 3.4.1 - Configuration Externalization (2025-07-16)
- **Configuration System**: Created comprehensive configuration management
  - CRUDConfig for main configuration with validation
  - SecurityConfig for security-specific settings
  - PerformanceConfig for monitoring thresholds
  - LoggingConfig for logging behavior
- **28 New Tests**: Added configuration validation and edge case tests
- **Backward Compatibility**: Default instances ensure existing code works unchanged

### Phase 3.3 - Logging Strategy Unification (2025-07-16)
- **Structured Logging**: Converted all log messages to structured format with `extra` parameters
- **Security-Aware Logging**: Implemented hashed user IDs and removed sensitive data
- **Comprehensive Guidelines**: Created `docs/logging-guidelines.md` with complete standards
- **Performance Monitoring**: Added query execution time tracking and slow query detection

### Phase 3.2 - Method Naming Standardization (2025-07-16)
- **Naming Convention Consistency**: Standardized all CRUD method names
- **Backward Compatibility**: Maintained existing API through method aliases
- **Documentation Standards**: Created `docs/naming-conventions.md`

### Phase 3.1 - Performance Optimization (2025-07-16)
- **Pagination System**: Scalable pagination with metadata
- **Strategic Database Indexes**: 4 performance-optimized indexes
- **New Filter Methods**: Optimized query methods for common use cases
- **Performance Monitoring**: Query execution time tracking

## Important Notes
- **Module Execution**: Run the application using `python -m app.main` for proper module resolution
- **Service Configuration**: Use dependency injection for services, defaults available for backward compatibility
- **Session Management**: The `CRUDUser` class automatically handles commits; avoid manual commit/rollback
- **Testing**: All tests use independent sessions; use appropriate fixtures for different scenarios
- **Performance**: Database indexes are optimized for common query patterns
- **Security**: Timing attack protection is configurable through SecurityConfig
- **Architecture**: The codebase follows service-oriented architecture with clean separation of concerns
- **Refactoring Progress**: Phase 3.4.2 complete (Security Service Separation) - significant architecture improvements implemented