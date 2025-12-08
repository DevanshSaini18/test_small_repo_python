# Service Layer (Business Logic & Data Access)

app/services.py implements transactional, database-backed operations and higher-level business rules on top of the ORM models. It centralizes CRUD operations, activity/usage logging, analytics, and composite behaviors used by API handlers.

Responsibilities & patterns:
- CRUD and list operations for Organization, User, Team, Item, Comment, Tag, APIKey, Webhook, and Activity/Usage logs.
- Transactional flow: create -> flush/extend relationships -> commit -> refresh; services take a Session and use domain models rather than raw SQL.
- Activity logging: log_activity is called by create/update/delete paths to record changes (details often JSON-encoded) for audit and UI feed functionality.
- Complex updates: update_item handles differential updates for assignees/tags (replacing associations), tracks field changes for activity logs, and sets completed_at when status flips to DONE.
- Analytics: get_item_analytics and get_usage_analytics aggregate counts (by status, priority), overdue/completed metrics, average completion time and usage statistics (request counts, endpoints, average response time, error rate).
- API key & webhook creation: generate_api_key is used to produce secure keys and webhooks persist secrets for signature verification.
- Item listing relies on status, priority, and assignee filters, with pagination controls for skip/limit.

Operational notes:
- Services assume proper authorization and org-scoped checks are enforced by higher-level dependencies/routes.
- Most functions return ORM instances (refreshed) for direct response serialization via Pydantic's orm_mode.
- Performance: queries use SQLAlchemy aggregates; larger datasets/pagination may need explicit indexing and optimized queries (see Data & Infra pages).

## Source Files
- app/services.py
- app/models.py
- app/auth.py
- app/schemas.py