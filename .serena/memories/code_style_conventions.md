# Code Style and Conventions

## Backend (Python)

### Code Formatting
- **Black**: Line length 88, Python 3.12 target
- **isort**: Black profile compatibility, line length 88
- **Type Hints**: Required for all function definitions (mypy enforced)
- **Docstrings**: Follow Python conventions

### Project Structure
```
backend/app/
├── api/v1/          # API endpoints organized by version
├── core/            # Core configuration (settings, security)
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic schemas for request/response
├── services/        # Business logic layer
├── repositories/    # Data access layer
└── utils/           # Utility functions
```

### Testing Structure
```
backend/tests/
├── unit/            # Unit tests for individual components
├── integration/     # API integration tests
├── performance/     # Performance and load tests
├── factories/       # Test data factories
└── utils/           # Test utilities
```

### Test Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `performance`: Performance tests
- `slow`: Slow-running tests
- `security`: Security-focused tests

## Frontend (TypeScript/React)

### Code Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Next.js configuration with strict rules
- **React 19**: Latest features with concurrent rendering
- **Tailwind CSS v4**: Utility-first CSS framework

### Project Structure
```
frontend/src/
├── app/            # Next.js app router pages
├── components/     # Reusable React components
├── lib/            # Utility libraries and API clients
├── hooks/          # Custom React hooks
└── types/          # TypeScript type definitions
```

## Database Conventions

### Migration Naming
```bash
alembic revision --autogenerate -m "Add user_id to revisions table"
alembic revision --autogenerate -m "Create approval_groups table"
```

### Model Naming
- Table names: snake_case plural (e.g., `approval_groups`)
- Column names: snake_case (e.g., `created_at`, `approver_id`)
- Foreign keys: `{table_name}_id` (e.g., `approval_group_id`)

## Environment Configuration

### Required Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration
- `SECRET_KEY`: JWT signing key
- `BACKEND_CORS_ORIGINS`: Allowed frontend origins
- `NEXT_PUBLIC_API_URL`: Backend API base URL for frontend