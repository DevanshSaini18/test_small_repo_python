## Services Layer (Business Logic)

The services layer (app/services.py) centralizes domain logic and DB interactions for organizations, users, teams, items, comments, tags, API keys, webhooks, activity logs, usage logging and analytics. All service functions accept an SQLAlchemy Session and operate on ORM models (app/models.py) with Pydantic request/response shapes defined in app/schemas.py.

Key responsibilities and patterns

- Transactional writes: create/update/delete operations use db.add/db.commit/db.refresh and occasionally db.flush to ensure relations (e.g., many-to-many assignees/tags) are persisted and IDs available.

- Schema-driven inputs: service creators and updaters accept Pydantic schema objects (e.g., OrganizationCreate, UserCreate, ItemCreate, ItemUpdate) and map fields to ORM models.

- Authentication helpers: password hashing and API key generation are delegated to auth utilities (app/auth.py) — create_user hashes passwords; create_api_key calls generate_api_key().

- Activity logging: log_activity(...) creates ActivityLog records for major domain events (create/update/delete/comment). Most mutating services call log_activity to persist audit entries.

- Relationship management: create_item and update_item explicitly manage many-to-many relations (assignees, tags) by querying the User/Tag models and assigning lists to db_item.assignees / db_item.tags. Team membership is handled similarly in add_user_to_team.

- Partial updates and change tracking: update_item uses ItemUpdate.dict(exclude_unset=True) to apply only changed fields, records old→new diffs in a changes dict, serializes changes to JSON and logs them via ActivityLog. It also sets completed_at when status becomes DONE.

- Query & filter patterns: read services use SQLAlchemy queries with optional filters (team_id, status, priority, assigned_to) and joins for assignee-based filtering. Pagination is supported via offset/limit.

- Aggregations & analytics: get_item_analytics and get_usage_analytics use SQLAlchemy func (count, avg) and in-memory aggregation to produce metrics such as by-status/by-priority counts, overdue counts, average completion time, request volumes, avg response time and error rate.

- Lightweight validators: read functions return Optional[T] or empty lists for missing/unauthorized resources (e.g., get_item returns None when not found; create_comment verifies item belongs to org).

Primary entry points (examples)

- Organization: create_organization, get_organization
- Users: create_user, get_user_by_email, get_users_by_organization
- Teams: create_team, add_user_to_team
- Items: create_item, get_item, get_items, update_item, delete_item
- Comments: create_comment, get_comments_by_item
- Tags: create_tag, get_tags
- API Keys / Webhooks: create_api_key, get_api_keys, create_webhook, get_webhooks
- Activity & Usage: log_activity, get_activity_logs, log_usage, get_usage_analytics

Source files


## Source Files
- app/services.py
- app/models.py
- app/schemas.py
- app/auth.py