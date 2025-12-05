# Getting Started

Welcome to the **FastAPI Todo SaaS** API! This guide will help you get the project up and running locally, understand the authentication flow, and make your first API call.

---

## Prerequisites

- **Python 3.11+**
- **Poetry** (or pip) for dependency management
- **Docker** (optional, for running the database)
- **Git**

## Clone the Repository

```bash
git clone https://github.com/your-org/fastapi-todo-saas.git
cd fastapi-todo-saas
```

## Install Dependencies

Using **Poetry**:

```bash
poetry install
poetry shell
```

Or with **pip**:

```bash
pip install -r requirements.txt
```

## Set Up the Database

The project uses **PostgreSQL**. You can run it locally via Docker:

```bash
docker run -d \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=todo_saas \
  -p 5432:5432 \
  postgres:15
```

Create the tables with Alembic migrations:

```bash
alembic upgrade head
```

## Run the Development Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Authentication

All protected endpoints require **JWT** or **API Key** authentication.

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"johndoe","password":"SecurePass123!","full_name":"John Doe","organization_id":1}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'
```

The response contains a **JWT token**. Save it for subsequent calls:

```json
{"access_token":"<token>","token_type":"bearer"}
```

### Using the Token

Add the token to the `Authorization` header:

```bash
-H "Authorization: Bearer <token>"
```

Alternatively, you can generate an **API Key** (admin only) and use the `X-API-Key` header.

---

## First API Call – Create an Item

```bash
curl -X POST http://localhost:8000/items \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "title":"Implement feature X",
        "description":"Detailed description",
        "status":"todo",
        "priority":"high",
        "due_date":"2025-12-31T23:59:59",
        "estimated_hours":8,
        "team_id":1,
        "assignee_ids":[2,3],
        "tag_ids":[1]
      }'
```

You should receive a JSON representation of the newly created item.

---

## Next Steps

- Explore the full **API Reference** (`docs/api-reference.md`).
- Generate an **API Key** for service‑to‑service communication.
- Review the **Architecture** document for deeper insight into the system design.

Happy coding! 🚀
