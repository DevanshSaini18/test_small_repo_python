# API Layer & Routing (HTTP Surface)

app/routes.py (mounted at /api/v1 in main.py) exposes the HTTP REST surface and maps incoming requests to service layer operations. main.py wires the router in and configures application-level middleware (CORS, logging, exception handling).

Major endpoint groups:
- Authentication: POST /auth/register, POST /auth/login, GET /auth/me — user registration, token issuance (JWT), and user info.
- Organizations: POST /organizations, GET /organizations/current, GET /organizations/{org_id}/users — create and read tenant info and membership lists.
- Teams: POST /teams, POST /teams/{team_id}/members/{user_id} — team creation and membership management (Admin only via dependency).
- Items (tasks): POST /items, GET /items/{item_id}, GET /items (filters: team_id/status/priority/assigned_to/skip/limit), PUT /items/{item_id}, DELETE /items/{item_id} — core task lifecycle. List endpoints now focus on typed filters without free-text search, matching the simplified service-layer query.
- Comments: POST /comments, GET /items/{item_id}/comments — commenting on items.
- Tags: POST /tags, GET /tags — tagging support.
- API Keys & Webhooks: Admin-only endpoints for managing API keys (/api-keys) and webhooks (/webhooks).
- Activity & Analytics: GET /activity, GET /analytics/items, GET /analytics/usage — auditing and operational analytics.

Important behaviors:
- Response models: Endpoints return Pydantic schemas (app/schemas.py) for consistent request/response shapes and validation.
- Auth & RBAC: Endpoints declare dependencies to enforce JWT-based authentication and role checks (require_role) or API key verification.
- Pagination & filtering: list endpoints support skip/limit and a set of typed filters that map to SQLAlchemy queries in services; the item list no longer exposes a search text parameter, so filtering is limited to explicit fields.
- Status codes: create operations use 201, deletes use 204, and routes raise HTTPException with appropriate codes on not-found/forbidden/unauthorized.

main.py highlights:
- Mounts router at /api/v1, creates DB tables at startup (Base.metadata.create_all), and configures middleware:
  - CORS (allow_origins=["*"] by default; production should restrict origins)
  - Request timing middleware that adds X-Process-Time header and logs request method/path/status/time
  - Global exception handler returning 500 with structured logging

## Source Files
- app/routes.py
- main.py
- app/services.py
- app/schemas.py
- app/dependencies.py