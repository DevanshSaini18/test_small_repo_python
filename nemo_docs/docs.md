# Automated Repository Summary

Purpose
- Enterprise Todo Platform is a production-ready, API-first SaaS todo/task system designed for multi-tenant organizations with enterprise features and a monetization path targeting $10M ARR. It focuses on team collaboration, RBAC security, analytics, and integrations.

Key features
- Multi-tenancy: organizations, subscription tiers (Free → Enterprise), teams, roles (Owner, Admin, Member, Viewer).
- Authentication & security: JWT auth, API keys, role-based access control, bcrypt password hashing, global exception handling, request logging.
- Advanced task management: priorities, statuses, due dates & overdue tracking, time tracking (estimated vs actual), subtasks, multi-user assignments, tags.
- Collaboration & audit: real-time comments, activity logs; mentions and attachments planned.
- Analytics & monitoring: item/status/priority reports, completion rates, average completion time, usage metrics, health endpoints.
- Integrations & API: RESTful API with OpenAPI/Swagger, webhooks, API key management, event-driven design.
- Enterprise readiness: CORS, health checks, monitoring, usage tracking, scalable deployment options (Docker, cloud-ready).

Installation
- Prereqs: Python 3.9+, Poetry (recommended) or pip.
- Quick install:
  - git clone <repo>
  - cd test_small_repo_python
  - poetry install (or pip install -r requirements.txt)
- Run:
  - Dev: uvicorn main:app --reload
  - Prod: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
- Docker:
  - Build: docker build -t enterprise-todo .
  - Run: docker run -p 8000:8000 enterprise-todo

Usage
- API base: http://localhost:8000/api/v1
- Docs: /docs (Swagger), /redoc
- Health: /health
- Common endpoints (examples):
  - Create organization: POST /organizations
  - Register user: POST /auth/register
  - Login: POST /auth/login → Bearer token
  - Create todo: POST /items (Authorization: Bearer YOUR_TOKEN)
  - Search items: GET /items?search_text=...&status=...
  - Analytics: GET /analytics/items

Project layout highlights: app/ (auth, models, routes, services), docs/, main.py, pyproject.toml. Tech stack: FastAPI, Python, SQLAlchemy, Pydantic, JWT (python-jose), bcrypt. Tests and some features are “coming soon.” License: MIT.

*This summary was automatically generated using OpenAI.*
