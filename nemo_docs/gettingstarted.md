# Getting Started

This guide walks through running the Enterprise Todo Platform locally, authenticating and making your first API request.

## Prerequisites
- Python 3.11+ (pyproject and .python-version)
- Poetry (recommended) or pip
- Docker (optional, for Postgres)
- Git

## Clone
```bash
git clone https://github.com/your-org/fastapi-todo-saas.git
cd fastapi-todo-saas
```

## Install dependencies
Using Poetry:
```bash
poetry install
poetry shell
```
Or pip:
```bash
pip install -r requirements.txt
```
(See pyproject.toml / requirements.txt)

## Configure environment
Copy `.env.example` to `.env` and update values (DATABASE_URL, SECRET_KEY, CORS_ORIGINS, etc.). The app reads common settings from environment variables defined in .env.example.

## Database
- Development default: SQLite (app/database.py uses sqlite:///./test.db).
- Production / Docker: PostgreSQL. Start via docker-compose (docker-compose.yml):
```bash
docker compose up -d db
```
Create schema using migrations (Alembic):
```bash
alembic upgrade head
```
Note: the app also calls Base.metadata.create_all(bind=engine) on startup (main.py) to create tables when using the bundled SQLite dev DB.

## Run the app
```bash
uvicorn main:app --reload
```
The API is available at http://localhost:8000 and docs at /docs. main.py sets CORS, request timing header X-Process-Time and a global exception handler.

## Authentication flow
- Register: POST /api/v1/auth/register (see app/routes.py)
- Login: POST /api/v1/auth/login returns JWT (app/auth.py handles token creation)
- Use token in requests: Authorization: Bearer <token>
- API Keys: Admins can create API keys and use X-API-Key header

## First API call — create an item
Example request (replace <token>):
```bash
curl -X POST http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Implement feature X","description":"Details","status":"todo","priority":"high","due_date":"2025-12-31T23:59:59","team_id":1,"assignee_ids":[2],"tag_ids":[1]}'
```
Response: JSON representation of the created item (routes and schemas define payloads).

## Next steps
- Review full API surface in docs/api-reference.md
- Generate API keys for service integrations
- Inspect app/services.py and app/models.py for business and data models

Referenced files: docs/getting-started.md, main.py, app/auth.py, app/routes.py, app/database.py, .env.example, docker-compose.yml, docs/api-reference.md


## Source Files
- docs/getting-started.md
- main.py
- app/auth.py
- app/routes.py
- app/database.py
- .env.example
- docker-compose.yml
- docs/api-reference.md