# Knowledge Revision System Overview

## Purpose
A system for submitting, reviewing, and approving revisions to knowledge base articles with a 5-status lifecycle (draft → submitted → approved/rejected/deleted).

## Tech Stack
**Backend**: Python 3.12+ with FastAPI, SQLAlchemy, PostgreSQL 17, Redis 3.0.504
**Frontend**: Next.js 14 (using Next.js 15.5.2) with TypeScript, React 19, Tailwind CSS v4
**Infrastructure**: Windows Server 2019 deployment (no Docker available)
**Package Management**: uv for Python, npm for Node.js

## Core Features
- Revision proposal management with approval workflows
- Approval groups for routing revisions
- Visual diff comparison of changes
- Notification system for status updates
- 6 core database tables: users, approval_groups, info_categories, articles, revisions, simple_notifications

## Environment Constraints
- Windows Server 2019 deployment (no Docker)
- Redis 3.0.504 (limited to basic operations)
- PostgreSQL 17 (full feature set)
- 26 business categories (01-26) for information classification