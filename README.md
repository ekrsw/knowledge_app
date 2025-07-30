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

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```

4. Copy environment configuration:
   ```bash
   copy ..\\.env.example .env
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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