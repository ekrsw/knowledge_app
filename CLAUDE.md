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
```

#### Running the Application
```bash
python app/main.py
```
Note: Currently runs as a demo script, not as an API server.

### Testing

#### Comprehensive Test Suite
The application features an extensive test suite with **123+ test methods** across **14 test files**, achieving **94% test coverage** of CRUD user operations:

**Test Categories:**
- **Basic Operations** (`test_crud_user_basic.py`) - Core CRUD functionality
- **Error Handling** (`test_crud_user_error_handling.py`) - Exception handling
- **Data Validation** (`test_crud_user_validation.py`) - Input validation and constraints
- **Security** (`test_crud_user_security.py`) - Password hashing, authentication, timing attacks
- **Optional Fields** (`test_crud_user_optional_fields.py`) - Field combinations and permissions
- **Edge Cases** (`test_crud_user_edge_cases.py`) - Boundary values, memory limits, concurrency
- **Transactions** (`test_crud_user_transactions.py`) - ACID properties, rollback, isolation
- **Integration** (`test_crud_user_integration.py`) - Real-world workflows, admin operations
- **Update Operations** (`test_crud_user_update.py`) - User update functionality
- **Password Updates** (`test_crud_user_update_password.py`) - Password change operations

#### Running Tests
```bash
pytest                          # Run all tests (123+ tests)
pytest -v                       # Verbose output
pytest --cov=app                # Run with coverage report
pytest tests/test_crud_user_security.py  # Run specific test file
pytest tests/test_crud_user_basic.py::TestCRUDUserBasic::test_create_user  # Run single test
```

#### Test Configuration
- **pytest.ini** configures async mode, test discovery, and disabled concurrent execution
- **conftest.py** provides three session fixtures:
  - `clean_db_session` - Cleans test data before/after (recommended)
  - `rollback_db_session` - Always rolls back
  - `simple_db_session` - Manual commit control

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
- `get_all_users()` - Retrieve all users
- `update_user_by_id()` - Update user information
- `update_password()` - Update user password with verification
- `delete_user()` - Delete user by ID

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
- Comprehensive error handling with custom exceptions
- Database migrations with Alembic
- User model with authentication and permission fields
- Extensive test suite with 94% coverage (123+ tests)
- Structured logging with operation tracking
- PostgreSQL-specific optimizations

### What's Missing
- FastAPI REST API endpoints and route handlers
- Authentication middleware (JWT tokens)
- API documentation (OpenAPI/Swagger)
- Production error handlers and middleware
- Code quality tools (linting, formatting, pre-commit hooks)
- API rate limiting and request validation
- Background task processing

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
- `docs/crud-user-refactoring-plan.md` - Comprehensive 3-phase refactoring plan with progress tracking
- Detailed docstrings in CRUD operations
- Type hints throughout the codebase for better IDE support

## Recent Changes (2025-07-15)
- **Phase 1.1 TOCTOU Implementation Completed**: Eliminated Time-of-Check-Time-of-Use race conditions by:
  - Removing pre-check methods (`_check_unique_constraints`)
  - Implementing PostgreSQL-specific error handling (pgcode 23505 for unique violations)
  - Adding comprehensive concurrency tests (`test_crud_user_concurrency.py`)
  - Modifying `create_user` and `update_user_by_id` to handle database-level constraint violations

## Important Notes
- **Character Encoding**: Use UTF8 for PostgreSQL connections when working with Japanese text
- **Session Management**: The `CRUDUser` class automatically handles commits; avoid manual commit/rollback
- **Testing**: All tests use independent sessions to prevent interference
- **Concurrency**: TOCTOU race conditions have been resolved using database-level constraints