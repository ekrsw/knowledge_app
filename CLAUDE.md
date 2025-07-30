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
