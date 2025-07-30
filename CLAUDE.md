# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Guidelines

This document defines the project's rules, objectives, and progress management methods. Please proceed with the project according to the following content.

## Top-Level Rules

- When you refer to this file, first shout “Hello Claude!!!!”.
- To maximize efficiency, **if you need to execute multiple independent processes, invoke those tools concurrently, not sequentially**.
- **You must think exclusively in English**. However, you are required to **respond in Japanese**.
- To understand how to use a library, **always use the Contex7 MCP** to retrieve the latest information.
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

The system uses a layered architecture:
- API Gateway Layer (authentication, rate limiting, error handling)
- Business Logic Layer (ProposalService, ApprovalService, DiffService, NotificationService)
- Data Access Layer (Repository pattern)
- Data Layer (PostgreSQL + Redis caching)

### Core Database Schema

The system manages 6 core tables:
- `users` - User management with approval group membership
- `approval_groups` - Approval responsibility assignment  
- `info_categories` - 26 real business categories (01-26)
- `articles` - Reference-only existing knowledge articles
- `revisions` - Revision proposals with 5-status lifecycle (draft → submitted → approved/rejected/deleted)
- `simple_notifications` - Basic notification system

### Development Environment Constraints

- **Windows Server 2019**: No Docker, Windows Service deployment
- **Redis 3.0.504**: Limited to basic key-value, Hash, List operations (no Streams, Modules)
- **PostgreSQL 17**: Can use latest features (partitioning, parallel queries)

### Key Design Principles

- Independent system (no existing knowledge base integration)
- Simplified workflow (5 statuses instead of complex multi-stage approval)
- After-only revision tracking (no before/after comparison, just proposed changes)
- Approval group-based routing (users belong to groups, articles require specific group approval)

### Common Development Commands

Currently no build/test commands are established. Implementation follows the 24-task breakdown in `.tmp/tasks.md` across 7 phases.
