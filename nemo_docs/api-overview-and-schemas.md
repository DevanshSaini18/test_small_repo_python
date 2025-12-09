# API Overview and Schemas

## API Surface
- **Base URL:** `http://localhost:8000/api/v1` and `/docs` for interactive Swagger UI.
- **Authentication:** `/auth/register`, `/auth/login`, `/auth/me`; all other endpoints require either a bearer JWT or `X-API-Key`. Admin-only routes use role enforcement (`require_role(UserRole.ADMIN)`).
- **Rate limiting:** tiered (Free: 100/min, Starter: 500/min, Professional: 2k/min, Enterprise: unlimited).

## Endpoint Groups
| Area | Key Routes | Notes |
| --- | --- | --- |
| Authentication | `/auth/register`, `/auth/login`, `/auth/me` | Creates/logs in users, returns JWT token payloads from `Token` schema. |
| Organizations | `/organizations`, `/organizations/current`, `/organizations/{id}/users` | Multi-tenant onboarding plus listing org users.
| Teams | `/teams`, `/teams/{team_id}/members/{user_id}` | Admin-only creation and membership management.
| Items | `/items`, `/items/{id}`, filters via query params (`team_id`, `status`, `priority`, `assigned_to`, `skip`, `limit`), update/delete APIs | CRUD plus filtering/pagination with RBAC via dependencies.
| Comments/Tags | `/comments`, `/items/{id}/comments`, `/tags` | Item-scoped comment creation and global tag management.
| API Keys & Webhooks | `/api-keys`, `/webhooks` | Admin-only key/webhook lifecycle plus event delivery documentation (HMAC-SHA256 signature).
| Activity & Analytics | `/activity`, `/analytics/items`, `/analytics/usage` | Logs and aggregated metrics (item status/priority breakdown, usage stats).

## Schema Coverage
- **Organizations:** `OrganizationBase`, `Create`, `Update`, `Read` expose subscription tiers, quotas, activation flags.
- **Users:** `UserBase`, `Create`, `Update`, `Read`, `Login`, plus `Token` for auth flows.
- **Teams/Tags/Items:** CRUD DTOs with nested relations (`ItemRead` surfaces assignees, tags, audit timestamps).
- **Comments/Attachments/Activity:** read/write schemas capture item linkage, authorship, metadata.
- **API Keys/Webhooks/Analytics:** DTOs describe key metadata, webhook payload/secrets, and analytics summaries (`ItemAnalytics`, `UsageAnalytics`).

Each route tightly maps to these Pydantic models (`app/routes.py`) and is documented in `docs/api-reference.md` for payload samples, filters, and error responses.

## Source Files
- docs/api-reference.md
- app/routes.py
- app/schemas.py