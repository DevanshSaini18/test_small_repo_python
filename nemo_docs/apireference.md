# API Reference

This API Reference summarizes the REST surface exposed by the Enterprise Todo Platform backend (see app/routes.py and docs/api-reference.md). It maps routes to request/response shapes (app/schemas.py), auth and access control (app/auth.py, app/dependencies.py, app/models.py), and service behavior (app/services.py). Interactive OpenAPI docs are served at /docs (main.py).

## Authentication

Supported methods (enforced in dependencies):
- JWT Bearer: Authorization: Bearer <token> — tokens created/verified via app/auth.py (create_access_token, decode_access_token).
- API Key: X-API-Key: <key> — validated by verify_api_key in app/dependencies.py and represented by APIKey model in app/models.py.

User roles (app/models.py) drive RBAC: owner, admin, member, viewer. Dependency require_role(...) enforces role hierarchy.

## Primary resource groups (routes implementation: app/routes.py)

- Authentication
  - POST /auth/register -> UserCreate -> UserRead
  - POST /auth/login -> Token
  - GET /auth/me -> current UserRead

- Organizations
  - POST /organizations -> OrganizationCreate -> OrganizationRead
  - GET /organizations/current -> OrganizationRead
  - GET /organizations/{org_id}/users -> List[UserRead]

- Teams
  - POST /teams (admin) -> TeamCreate -> TeamRead
  - POST /teams/{team_id}/members/{user_id} (admin)

- Items
  - POST /items -> ItemCreate -> ItemRead
  - GET /items/{item_id} -> ItemRead
  - GET /items -> List[ItemRead] (filters: team_id, status, priority, assigned_to, skip, limit)
  - PUT /items/{item_id} -> ItemUpdate -> ItemRead
  - DELETE /items/{item_id}

- Comments
  - POST /comments -> CommentCreate -> CommentRead
  - GET /items/{item_id}/comments -> List[CommentRead]

- Tags
  - POST /tags -> TagCreate -> TagRead
  - GET /tags -> List[TagRead]

- API Keys (admin)
  - POST /api-keys -> APIKeyCreate -> APIKeyRead
  - GET /api-keys -> List[APIKeyRead]

- Webhooks (admin)
  - POST /webhooks -> WebhookCreate -> WebhookRead
  - GET /webhooks -> List[WebhookRead]

- Activity
  - GET /activity -> List[ActivityLogRead] (optional item_id, limit)

- Analytics
  - GET /analytics/items -> ItemAnalytics (aggregates via app/services.py)
  - GET /analytics/usage?days=N (admin) -> UsageAnalytics

## Schemas and models

Request and response shapes are defined in app/schemas.py (Organization*, User*, Team*, Item*, Comment*, Tag*, APIKey*, Webhook*, ActivityLog*, analytics shapes). DB models live in app/models.py and include enums used by schemas: ItemStatus, PriorityLevel, UserRole, SubscriptionTier.

## Behavior notes (service layer)

Business logic, data validation and side-effects (activity logging, API key generation, analytics aggregation) are implemented in app/services.py. Examples: create_item adds assignees/tags and logs activity; get_item_analytics computes counts by status/priority and averages.

## Errors, rate limits, and webhooks

Standardized error responses (400/401/403/404/500) are documented in docs/api-reference.md. Rate limits are tiered by subscription tier (docs). Webhooks emit JSON events and include HMAC-SHA256 signature verification (X-Signature) using webhook secret (Webhook model).

Relevant files: app/routes.py, app/schemas.py, app/dependencies.py, app/services.py, app/auth.py, app/models.py, docs/api-reference.md, main.py


## Source Files
- app/routes.py
- app/schemas.py
- app/dependencies.py
- app/services.py
- app/auth.py
- app/models.py
- docs/api-reference.md
- main.py