# Task Completion Requirements

## Backend Task Completion

### Before Marking Complete
1. **Run all quality checks**:
   ```bash
   uv run black .                    # Code formatting
   uv run isort .                    # Import sorting
   uv run flake8 .                   # Linting
   uv run mypy .                     # Type checking
   ```

2. **Run relevant tests**:
   ```bash
   # For code changes
   DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/unit/ -v
   
   # For API changes
   DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/integration/ -v
   
   # For performance-critical changes
   DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/performance/ -v
   ```

3. **Database migration checks** (if schema changes):
   ```bash
   uv run alembic upgrade head       # Ensure migrations work
   uv run alembic history           # Verify migration history
   ```

## Frontend Task Completion

### Before Marking Complete
1. **Run quality checks**:
   ```bash
   npm run lint                     # ESLint checking
   npm run build                    # Build verification
   ```

2. **Manual testing**:
   - Verify functionality in development server: `npm run dev`
   - Test API connectivity via: `http://localhost:3000/api-test`

## Integration Testing

### Full System Verification
1. **Start backend**: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. **Start frontend**: `npm run dev`
3. **Test API connectivity**: Visit `http://localhost:3000/api-test`
4. **Expected results**: 6/8 tests should pass (2 auth-required endpoints will show "Unauthorized")

## Code Coverage Requirements

### Backend
- Maintain minimum 80% test coverage
- Run coverage report: `uv run pytest --cov=app --cov-report=html`
- Review coverage gaps in `htmlcov/index.html`

### Performance Validation
For performance-critical changes, run:
```bash
DATABASE_URL=sqlite+aiosqlite:///:memory: ENVIRONMENT=test uv run pytest tests/performance/ -v
```

## Documentation Updates
- Update relevant docstrings for new/modified functions
- Update type hints for all modified functions
- Consider updating README.md for significant architectural changes