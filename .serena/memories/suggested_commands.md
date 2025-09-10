# Suggested Commands for Knowledge Revision System

## Backend Development Commands

### Environment Setup
```bash
cd backend
uv sync --dev                           # Install dependencies
uv run                                  # Activate virtual environment
copy ..\.env.example .env              # Set up environment file
```

### Database Operations
```bash
uv run alembic upgrade head             # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create new migration
```

### Development Server
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Commands
```bash
# Run all tests
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest

# Run specific test categories
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/unit/ -v
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/integration/ -v
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/performance/ -v

# Run tests with coverage
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest --cov=app --cov-report=html

# Run specific test
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/integration/test_auth_api.py -v
```

### Code Quality Commands
```bash
uv run black .                          # Format code
uv run isort .                          # Sort imports
uv run flake8 .                         # Lint code
uv run mypy .                           # Type checking
```

## Frontend Development Commands

### Environment Setup
```bash
cd frontend
npm install                             # Install dependencies
```

### Development Server
```bash
npm run dev                             # Start development server with Turbopack
```

### Code Quality Commands
```bash
npm run lint                            # Run ESLint
npm run build                           # Build for production
npm start                               # Start production server
```

## API Testing
Access comprehensive API connection testing at:
```
http://localhost:3000/api-test
```

## Database Connection String Examples
For PostgreSQL: `DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_revision`
For SQLite (testing): `DATABASE_URL=sqlite+aiosqlite:///:memory:`