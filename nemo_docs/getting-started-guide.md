# Getting Started Guide

Quick path to running the FastAPI Todo SaaS stack locally and exercising its APIs.

## Local Setup
- **Prerequisites:** Python 3.11+, Poetry (or pip), Docker (optional), Git.
- **Clone:** `git clone https://github.com/your-org/fastapi-todo-saas.git && cd fastapi-todo-saas`.
- **Dependencies:** `poetry install && poetry shell` (or `pip install -r requirements.txt`).
- **PostgreSQL:** Run via Docker with `postgres:15`, then `alembic upgrade head` to apply migrations.
- **Run server:** `uvicorn main:app --reload`, API exposed at `http://localhost:8000`.

## Authentication Flow
- Register user via `/auth/register` POST with email, username, password, org.
- Log in via `/auth/login`, storing returned JWT (`access_token`).
- Attach bearer token (`Authorization: Bearer <token>`) to protected requests or use `X-API-Key` (admin-generated).

## First API Call
- POST `/items` with metadata (title, status, priority, due date, team, assignees, tags) to create work items.

## Next Steps
- Browse the full API surface in the **API Reference** (`docs/api-reference.md`).
- Generate API keys for service-to-service integrations and consult architecture materials for deeper context.


## Source Files
- docs/getting-started.md
- docs/api-reference.md