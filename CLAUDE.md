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

### Testing

#### Comprehensive Test Suite
The application features an extensive test suite with **55+ test methods** across **13 test files**, achieving **comprehensive coverage** of CRUD user operations:

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
pytest                          # Run all tests (99+ tests)
pytest -v                       # Verbose output
pytest --cov=app                # Run with coverage
pytest tests/test_crud_user_security.py  # Run specific test file
pytest tests/test_crud_user_basic.py::TestCRUDUserBasic::test_create_user  # Run single test
```

#### Key Testing Patterns
- **Async Session Management**: Fresh sessions with proper cleanup for each test
- **SQLAlchemy 2.0 Compatibility**: Immediate data retrieval pattern to avoid MissingGreenlet errors
- **Comprehensive Cleanup**: Automatic test data cleanup after each test
- **Security Focus**: Password hashing verification, timing attack resistance
- **Real-world Scenarios**: User registration workflows, admin operations, disaster recovery

## Architecture

### Layered Architecture
The application follows a clean layered architecture:

- **Models** (`app/models/`) - SQLAlchemy ORM models
- **Schemas** (`app/schemas/`) - Pydantic models for request/response validation
- **CRUD** (`app/crud/`) - Data access layer with async operations
- **Core** (`app/core/`) - Business logic, configuration, logging, security

### Async Pattern
- All database operations are async using SQLAlchemy 2.0
- Session management through `AsyncSessionLocal`
- Async context managers for database transactions

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
- `update_user()` - Update user information
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
- Database connection settings
- Logging configuration
- SQLAlchemy settings

## Development Patterns

### Creating New CRUD Operations
1. Define the operation in the appropriate CRUD class
2. Use async session management
3. Implement proper error handling and logging
4. Follow the existing naming conventions

### Database Schema Changes
1. Modify the model in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit the migration file if needed
4. Apply migration: `alembic upgrade head`

### Error Handling
- Use custom exceptions from `app/crud/exceptions.py`
- Implement pre-validation to avoid database-specific errors
- Log errors with appropriate context
- Handle rollback for failed transactions

## Current State

### Application Status
The application currently serves as a **CRUD operations demonstration** rather than a full REST API server. The `app/main.py` file acts as both the entry point and test runner for user management operations.

### What's Implemented
- Complete user management CRUD operations
- Async database operations with PostgreSQL
- Comprehensive error handling and logging
- Database migrations with Alembic
- User model with authentication fields and permissions
- **Extensive test suite with 99+ tests covering validation, security, edge cases, transactions, and integration scenarios**

### What's Missing
- FastAPI REST API endpoints
- Authentication middleware (JWT tokens)
- API route definitions
- OpenAPI/Swagger documentation
- Production-ready error handlers
- Code quality tools (linting, formatting)

## Security Notes
- Passwords are hashed using bcrypt via passlib with configurable cost factor
- Password verification functions available in `app.core.security`
- Database credentials are managed through environment variables
- UUID primary keys provide non-enumerable identifiers
- Security tests include timing attack resistance, password hash uniqueness, and sensitive data exposure prevention

## Testing Best Practices

### SQLAlchemy 2.0 Async Patterns
- Use immediate data retrieval before commit to avoid MissingGreenlet errors
- Store primitive types (strings, IDs) rather than ORM objects after commit
- Use `expire_on_commit=True` with proper data extraction patterns

### Test Structure
- Each test class creates fresh sessions with proper cleanup
- Use structured data dictionaries for post-commit verification
- Implement comprehensive cleanup methods to avoid test interference
- Follow naming conventions: `test_crud_user_<category>.py`

### Security Testing
- Verify password hashing with bcrypt format validation
- Test timing attack resistance for authentication operations
- Ensure no plain text passwords in logs or error messages
- Validate authentication workflows with active/inactive users