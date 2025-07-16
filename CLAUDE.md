# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **knowledge_app** - a Python-based web application built with **FastAPI** and **PostgreSQL**. It's designed as a user management system with authentication capabilities, implemented with modern async patterns and comprehensive error handling.

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
The application features an extensive test suite with **159 test methods** across **15+ test files**, achieving **94% test coverage** of CRUD user operations:

**Test Categories:**
- **Basic Operations** (`test_crud_user_basic.py`) - Core CRUD functionality
- **Error Handling** (`test_crud_user_error_handling.py`) - Exception handling
- **Data Validation** (`test_crud_user_validation.py`) - Input validation and constraints
- **Security** (`test_crud_user_security.py`) - Password hashing, authentication, timing attacks
- **Security Enhanced** (`test_crud_user_security_enhanced.py`) - Advanced security features
- **Optional Fields** (`test_crud_user_optional_fields.py`) - Field combinations and permissions
- **Edge Cases** (`test_crud_user_edge_cases.py`) - Boundary values, memory limits, concurrency
- **Transactions** (`test_crud_user_transactions.py`) - ACID properties, rollback, isolation
- **Integration** (`test_crud_user_integration.py`) - Real-world workflows, admin operations
- **Update Operations** (`test_crud_user_update.py`) - User update functionality
- **Password Updates** (`test_crud_user_update_password.py`) - Password change operations
- **Concurrency** (`test_crud_user_concurrency.py`) - Race condition and concurrent access tests
- **Type Safety** (`test_crud_user_type_safety.py`) - UUID type consistency tests
- **Pagination** (`test_crud_user_pagination.py`) - Performance optimization and pagination tests
- **Delete Operations** (`test_crud_user_delete.py`) - User deletion functionality
- **Index Performance** (`test_index_performance.py`) - Database index optimization verification

#### Running Tests
```bash
pytest                          # Run all tests (159 tests)
pytest -v                       # Verbose output
pytest --cov=app                # Run with coverage report
pytest --cov=app --cov-report=html  # Generate HTML coverage report
pytest tests/test_crud_user_security.py  # Run specific test file
pytest -k "test_create_user"    # Run tests matching pattern
pytest tests/test_crud_user_pagination.py  # Run pagination tests
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

### Layered Architecture
The application follows a clean layered architecture:

- **Models** (`app/models/`) - SQLAlchemy ORM models
- **Schemas** (`app/schemas/`) - Pydantic models for request/response validation
- **CRUD** (`app/crud/`) - Data access layer with async operations
- **Core** (`app/core/`) - Business logic, configuration, logging, security
- **Database** (`app/db/`) - Session management and initialization

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
- Comprehensive logging with request tracking
- Rollback handling for failed transactions

## Key Components

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
Pagination functionality introduced in Phase 3.1:
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

### Configuration
Settings managed through `app/core/config.py`:
- Environment-based configuration (development/testing/production)
- Database connection settings with async PostgreSQL URL
- Logging configuration with structured logging
- SQLAlchemy settings optimized for async operation

## Development Patterns

### Creating New CRUD Operations
1. Define the operation in the appropriate CRUD class
2. Use async session management with proper cleanup
3. Implement error handling using custom exceptions
4. Add comprehensive logging with operation context
5. Write tests covering all scenarios

### Database Schema Changes
1. Modify the model in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit the migration file if needed
4. Apply migration: `alembic upgrade head`
5. Update tests to cover new fields/constraints

### Testing Best Practices
- Use `clean_db_session` fixture for most tests
- Store primitive values (not ORM objects) after commit
- Implement comprehensive cleanup to avoid test interference
- Follow naming convention: `test_crud_user_<category>.py`
- Test both positive and negative scenarios

## Current State

### Application Status
The application currently serves as a **CRUD operations demonstration** rather than a full REST API server. The `app/main.py` file acts as both the entry point and test runner for user management operations.

### What's Implemented
- Complete user management CRUD operations with async patterns
- Pagination support for scalable data retrieval
- Comprehensive error handling with custom exceptions
- Database migrations with Alembic
- User model with authentication and permission fields
- Extensive test suite with 94% coverage (159 tests)
- Structured logging with operation tracking and performance monitoring
- PostgreSQL-specific optimizations and TOCTOU race condition fixes
- Security enhancements (timing attack resistance, information leak prevention)

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
- Passwords hashed using bcrypt with configurable cost factor (default: 12)
- UUID primary keys prevent enumeration attacks
- Timing attack resistant authentication operations
- Environment-based configuration for sensitive data
- No plain text passwords in logs or error messages
- Input validation at multiple layers (Pydantic + database constraints)

## Utility Scripts
- `check_tables.py` - Verify database table existence
- `PostgreSQL_Cheatsheet.md` - PostgreSQL command reference
- Various database creation scripts in root directory

## Documentation
- `docs/crud-user-refactoring-plan.md` - Comprehensive 3-phase refactoring plan with progress tracking (90% complete)
- `docs/index-optimization-analysis.md` - Database index optimization analysis and recommendations
- `docs/naming-conventions.md` - CRUD method naming standards and conventions
- `docs/logging-guidelines.md` - Comprehensive logging standards and best practices
- Detailed docstrings in CRUD operations
- Type hints throughout the codebase for better IDE support

## Recent Changes

### Phase 3.3 - Logging Strategy Unification (2025-07-16)
- **Structured Logging**: Converted all log messages to structured format with `extra` parameters
  - Replaced f-string logging with consistent structured format
  - Added operation context and error types to all log entries
  - Maintained security by using hashed user IDs and avoiding sensitive data
- **Comprehensive Guidelines**: Created `docs/logging-guidelines.md` with complete standards
- **Testing**: All 159 tests pass with updated logging verification

### Phase 3.2 - Method Naming Standardization (2025-07-16)
- **Naming Convention Consistency**: Standardized all CRUD method names
  - Renamed `delete_user()` → `delete_user_by_id()` for consistency
  - Created backward compatibility alias to maintain existing API
  - Documented naming standards in `docs/naming-conventions.md`
- **Code Updates**: Updated all usages across codebase and tests
- **Testing**: All 159 tests pass with zero regressions

### Phase 3.1 - Performance Optimization (2025-07-16)
- **Pagination Implementation**: Added scalable pagination support
  - `PaginationParams` and `PaginatedUsers` schemas
  - Enhanced `get_all_users()` with optional pagination
  - New `get_users_paginated()` method with metadata
- **Database Indexes**: Added strategic indexes for performance
  - `idx_users_is_active_true` - Partial index for active users
  - `idx_users_group` - Group filtering optimization
  - `idx_users_created_at_desc` - Recent users optimization
  - `idx_users_active_created_desc` - Composite index for complex queries
- **Performance Monitoring**: Query execution time tracking and slow query detection
- **New Methods**: Added optimized filter methods (`get_active_users`, `get_users_by_group`, `get_recent_users`)

### Phase 1-2 Completion (2025-07-15-16)
- **TOCTOU Race Conditions**: Eliminated Time-of-Check-Time-of-Use vulnerabilities
- **Security Enhancements**: Timing attack resistance, information leak prevention
- **Code Quality**: Eliminated duplications, improved error handling
- **Type Safety**: Consistent UUID type usage throughout

## Important Notes
- **Module Execution**: Run the application using `python -m app.main` for proper module resolution
- **Character Encoding**: Use UTF8 for PostgreSQL connections when working with Japanese text
- **Session Management**: The `CRUDUser` class automatically handles commits; avoid manual commit/rollback
- **Testing**: All tests use independent sessions to prevent interference. Some tests may have async event loop issues in certain environments
- **Concurrency**: TOCTOU race conditions have been resolved using database-level constraints
- **Pagination**: New pagination features maintain backward compatibility with existing code
- **Performance Monitoring**: Query execution times are automatically logged; slow queries (>500ms) generate warnings
- **Refactoring Status**: The codebase is currently 90% through a 3-phase refactoring plan. See `docs/crud-user-refactoring-plan.md` for detailed progress tracking
- **Method Naming**: All CRUD methods follow consistent `{action}_{entity}[_by_{identifier}]` pattern. See `docs/naming-conventions.md` for standards