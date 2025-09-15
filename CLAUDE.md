# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Knowledge System Approval Platform (KSAP)** - a full-stack application for managing knowledge maintenance proposals and approvals. The system enables users to create maintenance proposals, route them through approval workflows, and track changes with comprehensive diff analysis.

## Architecture

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI with async/await patterns
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Authentication**: JWT-based with role-based access control
- **API Structure**: RESTful API at `/api/v1` with comprehensive OpenAPI docs
- **API Specification**: Complete endpoint documentation available in `backend/API_SPECIFICATION.md`
- **Key Modules**:
  - `app/api/v1/endpoints/`: API route handlers (auth, users, proposals, approvals, etc.)
  - `app/core/`: Configuration, security, and exceptions
  - `app/utils/`: Business logic utilities (diff formatting, approval workflow)

### Frontend (Next.js 15 + React 19)
- **Framework**: Next.js 15 with App Router and Turbopack
- **Styling**: TailwindCSS v4
- **TypeScript**: Strict mode enabled
- **Architecture**: Sidebar navigation system (220px desktop, 180px tablet, hamburger mobile)
- **Structure**: App Router with comprehensive design documentation in `frontend/docs/`

## Development Commands

### Backend Setup & Development
```bash
cd backend

# Install dependencies (requires Python 3.12+)
uv sync --dev

# Database setup
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision_system uv run alembic upgrade head

# Development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/ -v
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/integration/ -v
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/performance/ -v

# Run single test
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/integration/test_auth_api.py::TestAuthUserInfo::test_get_current_user -v

# Code quality
uv run black .
uv run isort .
uv run flake8 .
uv run mypy .
```

### Frontend Setup & Development
```bash
cd frontend

# Install dependencies
npm install

# Development server (with Turbopack)
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Linting
npm run lint
```

## Database Management

### Alembic Migrations
```bash
# Create new migration
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision_system uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision_system uv run alembic upgrade head

# View migration history
uv run alembic history
```

### Environment Configuration
- Copy `.env.example` to `.env` and configure:
  - Database connection (PostgreSQL)
  - Redis configuration (for caching/sessions)
  - JWT secret keys
  - CORS origins for frontend

## Key Business Logic

### User Roles & Permissions
- **General Users**: Create and manage own maintenance proposals
- **Approvers**: Review and approve/reject proposals in assigned domains
- **Administrators**: Full system access including user management

### Core Workflows
1. **Proposal Creation**: Users submit knowledge maintenance proposals
2. **Approval Routing**: System routes proposals to appropriate approvers
3. **Review Process**: Approvers review diffs and make approval decisions with sidebar navigation
4. **Change Tracking**: System maintains comprehensive audit trails

### API Endpoints
For complete API endpoint documentation including request/response formats, authentication requirements, and role-based permissions, refer to `backend/API_SPECIFICATION.md`. Key endpoint groups:
- `/auth/*` - Authentication and user management
- `/proposals/*` - Maintenance proposal CRUD operations
- `/approvals/*` - Approval workflow management
- `/diffs/*` - Change analysis and diff generation
- `/revisions/*` - Historical maintenance tracking
- `/system/*` - Health checks and system statistics

## Testing Strategy

- **Unit Tests**: Core business logic and utilities
- **Integration Tests**: Full API endpoint testing with database
- **Performance Tests**: Load testing and memory usage validation
- Tests use SQLite in-memory database for speed and isolation
- Comprehensive test markers: `unit`, `integration`, `performance`, `slow`

## Code Conventions

### Backend (Python)
- **Style**: Black formatting, isort imports, flake8 linting
- **Type Hints**: Required for all functions (mypy enforced)
- **Async/Await**: Consistent async patterns throughout
- **Error Handling**: Structured exceptions in `app/core/exceptions.py`

### Frontend (TypeScript)
- **Strict TypeScript**: No implicit any types
- **Path Aliases**: `@/*` maps to project root
- **Component Structure**: App Router with TypeScript components

## Development Notes

- Backend runs on port 8000, frontend on port 3000
- Database migrations are version controlled in `backend/alembic/versions/`
- API documentation available at `http://localhost:8000/docs` (development)
- All database operations use async SQLAlchemy patterns
- JWT tokens expire after 8 days by default
- CORS configured for local development (localhost:3000, 3001)