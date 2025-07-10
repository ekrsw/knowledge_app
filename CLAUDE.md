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
- Database-specific error handling with pre-validation
- Comprehensive logging with request tracking

## Key Components

### User Management
The `CRUDUser` class in `app/crud/user.py` provides:
- `create_user()` - User creation with duplicate validation
- `get_user_by_id()` - Retrieve user by UUID
- `get_user_by_username()` - Retrieve user by username
- `get_user_by_email()` - Retrieve user by email
- `get_all_users()` - Retrieve all users

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

## Testing
The application currently uses `app/main.py` as a test runner for CRUD operations. Future FastAPI endpoints should be added to create a proper API server.

## Security Notes
- Passwords are hashed using bcrypt via passlib
- Database credentials are managed through environment variables
- UUID primary keys provide non-enumerable identifiers