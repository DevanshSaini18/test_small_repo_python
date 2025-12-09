# Architecture Overview
## Entry Point & Middleware
- `main.py` bootstraps the FastAPI app, exposes `/` and `/health`, configures CORS, attaches logging middleware that injects `X-Process-Time`, and wires up global exception handling plus router inclusion under `/api/v1`.
- Database tables are ensured by calling `Base.metadata.create_all(bind=engine)` during startup to keep the schema in sync with SQLAlchemy models.

## API Routing & Access Control
- `app/routes.py` defines grouped endpoints for auth, organizations, teams, items, comments, tags, API keys, webhooks, activity logs, and analytics, delegating to service functions while enforcing status codes and HTTP errors.
- Dependencies from `app/dependencies.py` inject the current user/organization, enforce RBAC via `require_role`, and validate API keys, ensuring each request carries a properly scoped session and multi-tenant context.

## Service & Business Logic Layer
- `app/services.py` encapsulates CRUD operations, tagging, commenting, webhook/API-key lifecycle, activity logging, and analytics calculations with SQLAlchemy sessions.
- Analytics cover status/priority breakdowns, overdue/completion trends, usage stats, and average response/error rates, while `log_activity`/`log_usage` keep audit trails tied to organizations and users.

## Data & Persistence
- `app/database.py` configures the SQLite engine, session factory, and request-scoped `get_db` generator consumed by FastAPI dependencies.
- `app/models.py` defines the multi-tenant schema (organizations, users, teams, items, comments, tags, API keys/webhooks, usage/activity logs) with enums for roles, status, priority, and subscription tiers, plus association tables for teams, tags, assignees.

## Security Helpers
- `app/auth.py` supplies password hashing, JWT creation/verification, and API key generation that underpin `routes` and `dependencies` for secure access.

## Source Files
- main.py
- app/routes.py
- app/services.py
- app/dependencies.py
- app/database.py
- app/models.py
- app/auth.py