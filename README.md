# Knowledge Revision System

A system for submitting, reviewing, and approving revisions to knowledge base articles.

## Architecture

**Backend**: Python 3.12+ with FastAPI, SQLAlchemy, PostgreSQL 17
**Frontend**: Next.js 14 with TypeScript, Tailwind CSS
**Infrastructure**: Windows Server 2019, Redis 3.0.504

## Project Structure

```
knowledge_app/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Core configuration
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Data access layer
│   │   └── utils/           # Utility functions
│   ├── tests/               # Backend tests
│   ├── alembic/            # Database migrations
│   └── pyproject.toml      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js app router
│   │   ├── components/     # React components
│   │   ├── lib/            # Utility libraries
│   │   ├── hooks/          # Custom React hooks
│   │   └── types/          # TypeScript types
│   ├── tests/              # Frontend tests
│   └── package.json        # Node.js dependencies
└── scripts/                # Deployment scripts
```

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 17
- Redis 3.0.504
- uv (Python package manager)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with uv:
   ```bash
   uv sync --dev
   ```

3. Activate virtual environment:
   ```bash
   uv run
   ```

4. Copy environment configuration:
   ```bash
   copy ..\\.env.example .env
   ```

5. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```

6. Start development server:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

### API Connection Testing

The frontend includes a comprehensive API connection testing tool to verify backend connectivity:

1. **Access the test page**:
   ```
   http://localhost:3000/api-test
   ```

2. **Available Tests**:
   - **🔗 基本接続テスト**: Tests system version endpoint connectivity
   - **🏥 ヘルスチェック**: Verifies API server health status
   - **📊 包括的テスト**: Tests 7 key endpoints (authentication-required endpoints will show "Unauthorized" - this is expected)
   - **🐛 デバッグ情報**: Displays system information and environment details

3. **Expected Results**:
   - **6/8 tests should pass** (2 authentication-required endpoints will fail without JWT tokens)
   - Response times should be under 20ms for local development
   - System info should display API version, build date, and available features

4. **Prerequisites for Testing**:
   - Backend server running on `http://localhost:8000`
   - Frontend server running on `http://localhost:3000`
   - PostgreSQL database connected and migrated

5. **Troubleshooting**:
   - If all tests fail: Check backend server is running
   - If connection timeout: Verify API base URL in `.env.local`
   - If 404 errors: Ensure database migrations are up to date

## Core Features

- **Revision Management**: Create, edit, and track knowledge revision proposals
- **Approval Workflow**: 5-status lifecycle (draft → submitted → approved/rejected/deleted)
- **Approval Groups**: Route revisions to appropriate approval groups
- **Diff Visualization**: Visual comparison of proposed changes
- **Notifications**: Real-time updates on revision status changes

## Database Schema

The system uses 6 core tables:
- `users` - User management with approval group membership
- `approval_groups` - Approval responsibility assignment
- `info_categories` - 26 business categories (01-26)
- `articles` - Reference-only existing knowledge articles
- `revisions` - Revision proposals with lifecycle management
- `simple_notifications` - Basic notification system

## Environment Constraints

- **Windows Server 2019**: No Docker, Windows Service deployment
- **Redis 3.0.504**: Limited to basic operations (no Streams/Modules)
- **PostgreSQL 17**: Full feature set available