## Data Model & Schemas

This project uses SQLAlchemy ORM for the canonical relational data model and Pydantic for request/response schemas. The database bootstrap provides a declarative Base and a per-request session dependency for FastAPI.

Key components (app/models.py)
- Association tables: user_teams, item_tags, item_assignees implement many-to-many relations between users-teams, items-tags, and items-assignees.
- Enums: PriorityLevel (low, medium, high, urgent), ItemStatus (todo, in_progress, in_review, done, archived), UserRole (owner, admin, member, viewer), SubscriptionTier (free, starter, professional, enterprise).
- Organization: core tenant entity with subscription_tier, quotas (max_users, max_items), is_active, timestamps. Relationships to users, teams, items, api_keys, webhooks, usage_logs. Cascades configured to delete-orphan for owned children.
- User: stores email/username/hashed_password, role, organization_id and relationships to teams (many-to-many), created_items, assigned_items (many-to-many), comments, activity_logs.
- Team: belongs to an Organization; members via user_teams; holds items.
- Tag: simple tag entity with name and color; many-to-many to Item via item_tags.
- Item: central work unit with title, description, status, priority, due_date, estimated/actual hours, relational fields (organization_id, team_id, created_by_id, parent_item_id), timestamps (created_at, updated_at, completed_at). Relationships: creator, assignees, tags, comments, attachments, activity_logs. Self-referential parent/ subtasks via parent_item and backref subtasks.
- Comment: content, item_id, author_id, timestamps; back-populates item and author.
- Attachment: filename, file_path, file_size, mime_type, item and uploaded_by relations.
- ActivityLog: generic audit entries (action, entity_type, entity_id, details JSON string), linked to user and optionally item.
- APIKey: org-scoped secrets with key, name, is_active, last_used_at, expires_at.
- Webhook: url, events (comma-separated), secret for verification, is_active.
- UsageLog: per-organization request telemetry (endpoint, method, status_code, response_time_ms, timestamp).

Pydantic schemas (app/schemas.py)
- Mirror the models with Base / Create / Update / Read variants for major entities: Organization, User, Team, Tag, Item, Comment, Attachment, ActivityLog, APIKey, Webhook.
- Read schemas enable orm_mode to serialize SQLAlchemy objects. Nested relationships are represented (e.g., ItemRead includes assignees: List[UserRead], tags: List[TagRead]).
- ItemCreate supports team_id, parent_item_id, assignee_ids, tag_ids. ItemUpdate exposes partial updates including status, priority, assignee_ids, tag_ids.
- Auth/session schemas include Token and UserLogin types.
- Analytics schemas: ItemAnalytics and UsageAnalytics summarize computed metrics for dashboards.

Database bootstrap (app/database.py)
- SQLAlchemy engine and SessionLocal configured (default SQLALCHEMY_DATABASE_URL = sqlite:///./test.db). Declarative Base exported as Base. get_db() yields a request-scoped SessionLocal for dependency injection in FastAPI routes/services.

## Source Files
- app/models.py
- app/schemas.py
- app/database.py