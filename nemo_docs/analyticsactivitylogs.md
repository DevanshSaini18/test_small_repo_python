## Analytics & Activity Logs

Overview

The project captures operational and business-oriented telemetry via two primary subsystems: Activity Logs (domain-level events tied to users/items) and Usage Logs (API request-level metrics). These are persisted in the relational schema and exposed through service functions and REST endpoints for retrieval and basic aggregation.

Data model

- ActivityLog (app/models.py)
  - Fields: id, action (e.g. created, updated, deleted, commented), entity_type (item, comment, user, ...), entity_id, details (JSON string), user_id, item_id (nullable), created_at.
  - Relationships: links to User and Item; organization association inferred through the user->organization relationship when querying.

- UsageLog (app/models.py)
  - Fields: id, organization_id, endpoint, method, status_code, response_time_ms, timestamp.
  - Relationship: organization back-reference used for per-organization usage aggregation.

Activity logging flow (services)

- log_activity(db, action, entity_type, entity_id, user_id=None, item_id=None, details=None) (app/services.py)
  - Creates and commits an ActivityLog row. Called from service operations (create_user, create_team, create_item, update_item, delete_item, create_comment, etc.) whenever an auditable change occurs.
  - Details parameter is used to store change diffs (e.g. assignees or field changes) as a JSON string.

Retrieval

- get_activity_logs(db, org_id, item_id=None, limit=50) (app/services.py)
  - Joins ActivityLog -> User and filters by User.organization_id to constrain results to an organization.
  - Supports optional item_id filter and returns recent entries ordered by created_at desc (limit default 50).

- Routes: GET /activity (app/routes.py)
  - Query params: item_id (optional), limit (default 50, max 500)
  - Authentication: any active user in organization (get_current_active_user). Response model: List[ActivityLogRead] (app/schemas.py).

Item analytics (business metrics)

- get_item_analytics(db, org_id) (app/services.py)
  - Computes: total_items, counts broken down by Item.status (by_status) and PriorityLevel (by_priority), overdue_items (due_date < now and not DONE), completed_this_week (completed_at within last 7 days), avg_completion_time_hours (avg of actual_hours where present).
  - Uses SQL aggregation (func.count, func.avg) and iterates enums for bucketed counts.

- Route: GET /analytics/items (app/routes.py)
  - Authentication: any active user in org. Response model: ItemAnalytics (app/schemas.py) with shape: total_items, by_status, by_priority, overdue_items, completed_this_week, avg_completion_time_hours.

Usage analytics and logging

- log_usage(db, org_id, endpoint, method, status_code, response_time_ms) (app/services.py)
  - Persists a UsageLog row per API request (intended to be called by middleware or wrapped request handlers).

- get_usage_analytics(db, org_id, days=7) (app/services.py)
  - Aggregates UsageLog entries since (now - days) and returns: total_requests, requests_by_endpoint (counts per endpoint), avg_response_time_ms, error_rate (% of requests with status_code >= 400).

- Route: GET /analytics/usage (app/routes.py)
  - Query param: days (1..90, default 7)
  - Authentication: Admin-only (require_role(UserRole.ADMIN)). Response model: UsageAnalytics (app/schemas.py).

Schemas (app/schemas.py)

- ActivityLogRead: id, action, entity_type, entity_id, details, user_id, created_at (ORM mode).
- ItemAnalytics: total_items, by_status (dict), by_priority (dict), overdue_items, completed_this_week, avg_completion_time_hours.
- UsageAnalytics: total_requests, requests_by_endpoint (dict), avg_response_time_ms, error_rate.

API reference

- docs/api-reference.md documents the endpoints: GET /activity, GET /analytics/items, GET /analytics/usage with example responses and notes about role restrictions (usage analytics requires admin).

Relevant source files

- app/models.py
- app/services.py
- app/schemas.py
- app/routes.py
- docs/api-reference.md


## Source Files
- app/models.py
- app/services.py
- app/schemas.py
- app/routes.py
- docs/api-reference.md