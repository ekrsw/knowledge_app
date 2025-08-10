# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Guidelines

This document defines the project's rules, objectives, and progress management methods. Please proceed with the project according to the following content.

## Top-Level Rules

- When you refer to this file, first shout “Hello Claude!!!!”.
- To maximize efficiency, **if you need to execute multiple independent processes, invoke those tools concurrently, not sequentially**.
- **You must think exclusively in English**. However, you are required to **respond in Japanese**.
- To understand how to use a library, **always use the Context7 MCP** to retrieve the latest information.
- For temporary notes for design, create a markdown in `.tmp` and save it.
- **After using Write or Edit tools, ALWAYS verify the actual file contents using the Read tool**, regardless of what the system-reminder says. The system-reminder may incorrectly show "(no content)" even when the file has been successfully written.
- Please respond critically and without pandering to my opinions, but please don't be forceful in your criticism.

## Programming Rules

### Required Reading
- [Coding Guidelines](.claude/coding_style/CODING_GUIDELINES.md) - Basic coding standards and conventions
- [Security Guidelines](.claude/coding_style/SECURITY.md) - Security requirements and implementation
- [Testing Strategy](.claude/coding_style/TESTING.md) - Testing methodologies and coverage requirements
- [Performance Guidelines](.claude/coding_style/PERFORMANCE.md) - Efficient implementation guide
- [API Design Guidelines](.claude/coding_style/API_DESIGN.md) - RESTful API design best practices

## Development Style - Specification-Driven Development

### Overview

When receiving development tasks, please follow the 4-stage workflow below. This ensures requirement clarification, structured design, and efficient implementation.

### 4-Stage Workflow

#### Stage 1: Requirements

- Analyze user requests and convert them into clear functional requirements
- Document requirements in `.tmp/requirements.md`
- Use `/requirements` command for detailed template

#### Stage 2: Design

- Create technical design based on requirements
- Document design in `.tmp/design.md`
- Use `/design` command for detailed template

#### Stage 3: Task List

- Break down design into implementable units
- Document in `.tmp/tasks.md`
- Use `/tasks` command for detailed template
- Manage major tasks with TodoWrite tool

#### Stage 4: Implementation

- Implement according to task list
- For each task:
  - Update task to in_progress using TodoWrite
  - Execute implementation and testing
  - Run lint and typecheck
  - Update task to completed using TodoWrite

### Workflow Commands

- `/spec` - Start the complete specification-driven development workflow
- `/requirements` - Execute Stage 1: Requirements only
- `/design` - Execute Stage 2: Design only (requires requirements)
- `/tasks` - Execute Stage 3: Task breakdown only (requires design)

### Important Notes

- Each stage depends on the deliverables of the previous stage
- Please obtain user confirmation before proceeding to the next stage
- Always use this workflow for complex tasks or new feature development
- Simple fixes or clear bug fixes can be implemented directly

## Project: Knowledge Revision Approval System

### Architecture Overview

This is a knowledge revision proposal and approval system built with:

**Backend**: Python 3.12+ with FastAPI 0.115.8, SQLAlchemy 2.0.40, PostgreSQL 17
**Frontend**: Next.js 14 with TypeScript, Tailwind CSS
**Infrastructure**: Windows Server 2019, Redis 3.0.504 (legacy constraints)

The system uses a layered architecture following FastAPI best practices:

**API Layer** (`app/api/v1/endpoints/`):
- RESTful endpoints organized by domain (articles, revisions, users, etc.)
- JWT authentication with role-based access control
- Request/response validation with Pydantic schemas

**Business Logic Layer** (`app/services/`):
- `ProposalService`: Revision proposal lifecycle management
- `ApprovalService`: Approval workflow and status transitions
- `DiffService`: Change detection and comparison logic
- `NotificationService`: User notification and communication

**Data Access Layer** (`app/repositories/`):
- Repository pattern with async SQLAlchemy 2.0
- Generic base repository with common CRUD operations
- Domain-specific repositories for complex queries

**Models & Schemas** (`app/models/`, `app/schemas/`):
- SQLAlchemy 2.0 models with modern Mapped types
- Pydantic schemas for API validation and serialization
- Clear separation between database models and API schemas

**Core Infrastructure** (`app/core/`, `app/database.py`):
- Configuration management with Pydantic Settings
- JWT security implementation
- Database connection and session management
- Custom exception handling

### Core Database Schema

The system manages 6 core tables with the following relationships:

**Core Entities:**
- `users` (UUID PK): User management with role-based access (user/approver/admin)
- `approval_groups` (UUID PK): Group-based approval responsibility assignment
- `info_categories` (UUID PK): Business knowledge categories for content classification
- `articles` (string PK): Reference-only existing knowledge articles (independent of external systems)

**Workflow Entities:**
- `revisions` (UUID PK): Revision proposals with 5-status lifecycle:
  - `draft` → `submitted` → `approved`/`rejected`/`deleted`
  - Required `approver_id` field (not nullable)
  - After-only change tracking (no before/after comparison)
  - Links to target article via `target_article_id` (non-FK for flexibility)
- `simple_notifications` (UUID PK): Basic notification system for workflow updates

**Key Relationships:**
- Users belong to approval groups (many-to-many potential)
- Articles are assigned to specific approval groups for routing
- Revisions require both proposer and approver (both link to users table)
- Notifications track revision status changes

### Development Environment Constraints

- **Windows Server 2019**: No Docker, Windows Service deployment
- **Redis 3.0.504**: Limited to basic key-value, Hash, List operations (no Streams, Modules)
- **PostgreSQL 17**: Can use latest features (partitioning, parallel queries)

### Mixed Permission Model (January 2025 Update)

**New Permission Matrix:**
| Status | Admin | All Auth Users | Creator Only |
|--------|-------|---------------|-------------|
| submitted | ✓ | ✓ | - |
| approved | ✓ | ✓ | - |
| draft | ✓ | - | ✓ |
| rejected | ✓ | - | ✓ |

**Key Benefits:**
- **Transparency**: Submitted/approved revisions visible to all authenticated users
- **Privacy Protection**: Draft/rejected revisions only accessible to creators
- **Knowledge Sharing**: Approved changes serve as reference for future revisions

### Key Design Principles

- Independent system (no existing knowledge base integration)
- Simplified workflow (5 statuses instead of complex multi-stage approval)
- After-only revision tracking (no before/after comparison, just proposed changes)
- Approval group-based routing (users belong to groups, articles require specific group approval)
- Mixed permission model for transparency and privacy balance

### Common Development Commands

**Environment Setup:**
```bash
# Install dependencies with uv
uv install

# Set up environment variables
cp .env.example .env  # Edit with actual values

# Database migrations
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision uv run alembic upgrade head

# Generate new migration
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision uv run alembic revision --autogenerate -m "Migration description"
```

**Development:**
```bash
# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests (recommended pattern used in project)
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest backend/tests/ -v

# Run specific integration tests
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest backend/tests/integration/test_revisions_api.py -v

# Quick test validation (no traceback)
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest backend/tests/integration/ -q --tb=no

# Run with coverage
uv run pytest --cov=app

# Code formatting and linting
uv run black app/
uv run isort app/
uv run flake8 app/
uv run mypy app/
```

**Database Access:**
```bash
# Connect to PostgreSQL database
psql "postgresql://postgres:password@localhost:5432/knowledge_revision"

# Check database tables
psql "postgresql://postgres:password@localhost:5432/knowledge_revision" -c "\d"
```

### Recent Major Updates (January 2025)

#### Mixed Permission Model Implementation
The system now uses a mixed permission model for revision access control:
- **Public Revisions** (submitted/approved): Accessible to all authenticated users
- **Private Revisions** (draft/rejected): Only accessible to the creator and admin users

**Key Repository Methods Added:**
- `get_mixed_access_revisions()`: Returns public revisions + user's private revisions
- `get_public_revisions()`: Returns only submitted/approved revisions  
- `get_user_private_revisions()`: Returns user's draft/rejected revisions
- `get_public_revisions_by_article()`: Returns public revisions for specific article

#### New API Endpoints

**Article-Specific Revisions (January 2025):**
```http
GET /api/v1/revisions/by-article/{target_article_id}
```
- **Purpose**: Get public revisions (submitted/approved) for a specific article
- **Access**: All authenticated users
- **Use Cases**: Article history display, reference for new revisions
- **Implementation**: `backend/app/repositories/revision.py:get_public_revisions_by_article()`

### Important File Locations

**Core Implementation Files:**
- `backend/app/repositories/revision.py` - Mixed permission model implementation
- `backend/app/api/v1/endpoints/revisions.py` - Revision API endpoints  
- `backend/tests/integration/test_revisions_api.py` - Comprehensive test coverage
- `.tmp/api_design.md` - Complete API specification
- `.tmp/design.md` - Technical design documentation
- `.tmp/test_design.md` - Test design specifications

**Configuration:**
- `.claude/settings.local.json` - Tool permissions and project settings
- `backend/.env.example` - Environment configuration template

### Key Technical Patterns

**Permission Checking Pattern:**
```python
# Use mixed access model for listings
if user.role == "admin":
    revisions = await revision_repository.get_all(db, skip=skip, limit=limit)
else:
    revisions = await revision_repository.get_mixed_access_revisions(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
```

**Test Execution Pattern:**
```bash
# Always use in-memory SQLite for tests with environment variables
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest [test_path] -v
```

### Architecture Notes

**After-Only Design:**
- Revisions store only the proposed changes (`after_*` fields)
- Original data comes from the `articles` table
- Differences are computed dynamically for display

**Status Workflow:**
```
draft → submitted → approved/rejected/deleted
  ↑         ↓
  └─────────┘ (withdraw)
```

**Repository Pattern:**
- Generic base repository with common CRUD operations
- Domain-specific repositories inherit from base
- Async/await throughout for performance

### Project-Specific Best Practices

#### Database Schema Considerations
- `target_article_id` in revisions is **NOT** a foreign key for flexibility
- `approver_id` is **required** (not nullable) - revisions must have designated approvers
- All UUIDs use `uuid_generate_v4()` for generation
- `after_*` fields in revisions table can be NULL (only changed fields are set)

#### Test Implementation Standards
- Use descriptive test class names: `TestRevisionsByArticle`, `TestRevisionList`
- Test coverage includes: happy path, edge cases, authentication, authorization
- Always test with multiple user roles (user, approver, admin)
- Use factory patterns for test data creation
- Expect 403 (Forbidden) for unauthorized access, not 401 (Unauthorized)

#### Error Handling Patterns
```python
# Custom exceptions with appropriate HTTP status codes
raise ProposalNotFoundError("Revision not found")  # 404
raise ProposalPermissionError("Insufficient permissions")  # 403
raise ProposalStatusError("Invalid status transition")  # 400
```

#### Service Layer Responsibilities
- **ProposalService**: Handles business logic, validation, state transitions
- **ApprovalService**: Manages approval workflow, metrics, bulk operations
- **DiffService**: Generates comparisons between articles and revisions
- **NotificationService**: Creates and manages user notifications

#### API Endpoint Naming Convention
- Use plural nouns: `/revisions/`, `/users/`, `/articles/`
- Group related operations: `/revisions/by-article/{id}`, `/revisions/by-status/{status}`
- Separate CRUD operations (`/revisions/`) from business logic (`/proposals/`)

### Troubleshooting Common Issues

#### Test Failures
```bash
# If tests fail due to database issues, check environment variables
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test

# For specific test debugging, use -v flag and class::method notation
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest backend/tests/integration/test_revisions_api.py::TestRevisionsByArticle::test_get_revisions_by_article_public_only -v
```

#### Permission Issues
- Check user roles: 'user', 'approver', 'admin'
- Verify approval_group_id assignments
- Ensure revision.approver_id matches current user for approval operations

#### Database Migration Issues
```bash
# Generate migration with specific message
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision uv run alembic revision --autogenerate -m "Descriptive migration message"

# Check migration status
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision uv run alembic current

# Apply migrations
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision uv run alembic upgrade head
```

### Documentation References

For detailed specifications, always refer to:
1. `.tmp/api_design.md` - Complete API endpoint documentation
2. `.tmp/design.md` - System architecture and technical design
3. `.tmp/test_design.md` - Testing strategies and patterns
4. `backend/tests/` - Live examples of implementation patterns

### Windows Server Deployment Notes

- Use `uv` for dependency management (not pip/virtualenv)
- Configure Windows services for production deployment
- Redis 3.0.504 limitations: No Streams, no Modules, basic operations only
- PostgreSQL 17 can use modern features (async, JSON operations, partitioning)
