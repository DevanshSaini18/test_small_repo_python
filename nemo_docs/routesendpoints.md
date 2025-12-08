## Routes & Endpoints

This module (app/routes.py) defines the FastAPI HTTP surface for the Enterprise Todo Platform. Routes are organized by feature area and delegate business logic to the service layer (app/services.py). Request/response validation and shapes are expressed with Pydantic schemas (app/schemas.py). Security and multi-tenant access control rely on dependencies in app/dependencies.py and authentication helpers in app/auth.py.

Key characteristics
- Grouped by responsibility: Authentication, Organizations, Teams, Items, Comments, Tags, API Keys, Webhooks, Activity, Analytics.
- Dependency-based access control: get_current_active_user, get_current_organization, require_role(UserRole.ADMIN) are applied per-route to enforce authentication, organization scoping, and RBAC.
- Consistent response models and status codes: decorator-level response_model and status_code annotations (e.g., 201 CREATED for creates, 204 NO_CONTENT for deletes).
- Filtering, paging, and validation: List endpoints use Query parameters (e.g., /items supports team_id, status, priority, assigned_to, skip, limit). Analytics endpoints accept constrained query params (days between 1 and 90).
- Error handling: Routes raise HTTPException with appropriate HTTP status codes when services indicate not-found, unauthorized or invalid states.

Representative endpoints
- Authentication
  - POST /auth/register -> UserCreate -> UserRead (201)
  - POST /auth/login -> UserLogin -> Token (JWT) on success
  - GET /auth/me -> current user (requires bearer token)

- Organization
  - POST /organizations -> OrganizationCreate -> OrganizationRead (201)
  - GET /organizations/current -> OrganizationRead (scoped to current user)
  - GET /organizations/{org_id}/users -> List[UserRead] (ensures current user belongs to org)

- Teams (Admin)
  - POST /teams -> TeamCreate -> TeamRead (201)
  - POST /teams/{team_id}/members/{user_id} -> add user to team

- Items
  - POST /items -> ItemCreate -> ItemRead (201)
  - GET /items/{item_id} -> ItemRead
  - GET /items -> List[ItemRead] (filters: team_id, status, priority, assigned_to; pagination via skip & limit)
  - PUT /items/{item_id} -> ItemUpdate -> ItemRead
  - DELETE /items/{item_id} -> 204 NO_CONTENT

- Comments & Tags
  - POST /comments -> CommentCreate -> CommentRead (201)
  - GET /items/{item_id}/comments -> List[CommentRead]
  - POST /tags -> TagCreate -> TagRead (201)
  - GET /tags -> List[TagRead]

- API Keys & Webhooks (Admin)
  - POST /api-keys, GET /api-keys
  - POST /webhooks, GET /webhooks

- Activity & Analytics
  - GET /activity -> List[ActivityLogRead] (optional item_id, limit)
  - GET /analytics/items -> ItemAnalytics
  - GET /analytics/usage -> UsageAnalytics (Admin, days query param)

Interactions with other modules
- app/services.py: performs DB operations and domain logic invoked by routes.
- app/schemas.py: defines request/response Pydantic models used in route signatures.
- app/dependencies.py & app/auth.py: implement authentication, JWT creation/validation, API key validation and RBAC.
- app/models.py / app/database.py: underlying ORM models and DB session used by services invoked from routes.

Source files


## Source Files
- app/routes.py
- app/services.py
- app/schemas.py
- app/dependencies.py
- app/auth.py
- app/models.py
- app/database.py