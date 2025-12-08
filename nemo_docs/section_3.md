# API Layer & Routing (HTTP Surface)

app/routes.py (mounted at /api/v1 in main.py) exposes the HTTP REST surface and maps incoming requests to service layer operations. main.py wires the router in and configures application-level middleware (CORS, logging, exception handling).

Major endpoint groups:
- Authentication: POST /auth/register, POST /auth/login, GET /auth/me — user registration, token issuance (JWT), and user info.
- Organizations: POST /organizations, GET /organizations/current, GET /organizations/{org_id}/users — create and read tenant info and membership lists.
- Teams: POST /teams, POST /teams/{team_id}/members/{user_id} — team creation and membership management (Admin only via dependency).
- Items (tasks): POST /items, GET /items/{item_id}, GET /items (filters: team_id/status/priority/assigned_to/skip/limit), PUT /items/{item_id}, DELETE /items/{item_id} — core task lifecycle, with text-based search removed from the service layer, leaving the remaining filters to map to SQLAlchemy queries.
- Comments: POST /comments, GET /items/{item_id}/comments — commenting on items.
- Tags: POST /tags, GET /tags — tagging support.
- Notifications: POST /notifications/due-reminders, POST /notifications/overdue — admin-triggered reminder and overdue alert dispatch via notification_service.
- Exports: GET /export/items/csv, GET /export/items/json, GET /export/activity-log/csv — export endpoints that stream CSV/JSON attachments using fastapi.responses.Response and export_service, honoring organization scope, filters (team/status/priority), include_comments flag, and admin-only limits on activity logs.
- Reports: GET /reports/team/{team_id}, GET /reports/user/{user_id}, GET /reports/organization — report generation APIs backed by export_service, with user-level safeguards (users can only view their own report unless admin) and admin-only organization summaries.
- API Keys & Webhooks: Admin-only endpoints for managing API keys (/api-keys) and webhooks (/webhooks).
- Activity & Analytics: GET /activity, GET /analytics/items, GET /analytics/usage — auditing and operational analytics.

Important behaviors:
- Response models: Endpoints return Pydantic schemas (app/schemas.py) for consistent request/response shapes and validation, while export/download endpoints return streaming Response objects with appropriate content-disposition headers.
- Auth & RBAC: Endpoints declare dependencies to enforce JWT-based authentication and role checks (require_role) or API key verification, including new admin-only report/export/notification routes and user-scoped report access.
- Pagination & filtering: list endpoints support skip/limit and the supported typed filters that map to SQLAlchemy queries in services (team/status/priority/assigned_to only, without the prior title/description text search).
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