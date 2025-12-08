# Core Data Models (Domain Layer)

Source of truth for the application's data model and multi-tenant domain logic. app/models.py defines the SQLAlchemy ORM layer that represents organizations, users, teams, items (tasks), tags, comments, attachments, activity logs, API keys, webhooks, and usage logs.

Key points:
- Multi-tenancy: Organization is the top-level tenant; most entities carry organization_id and relationships are constrained with ondelete cascades so tenant deletion removes related data.
- Enums used to capture domain states: PriorityLevel (low/medium/high/urgent), ItemStatus (todo, in_progress, in_review, done, archived), UserRole (owner/admin/member/viewer), SubscriptionTier (free/starter/professional/enterprise).
- Associations: Many-to-many relationships are explicit via association tables user_teams, item_tags, item_assignees to model teams, tags, and assignees.
- Items: Rich task model with parent/child self-referential relationship for subtasks, assignees, tags, attachments, timestamps (created_at/updated_at/completed_at), estimated/actual hours and priority/status fields.
- Activity and usage: ActivityLog tracks user actions (created/updated/deleted/commented) with JSON details; UsageLog captures request-level metrics by organization for analytics.
- API keys & Webhooks: APIKey model stores sk_-style keys with expiry and last_used, Webhook stores endpoint, events, secret for signature verification.
- Constraints & cascade behaviour: ForeignKeys use ondelete CASCADE/SET NULL aligned with expected semantics (e.g., deleting a user or organization cleans up related items or sets created_by to null where appropriate).

Why it matters:
This file encapsulates the domain shape and database constraints that the rest of the app (services, routes, analytics) rely on. Any change here impacts migrations, queries, and RBAC/enforcement logic.


## Source Files
- app/models.py