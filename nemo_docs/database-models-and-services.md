# Database Models & Services

## Models overview
- **Enums & associations**: `PriorityLevel`, `ItemStatus`, `UserRole`, `SubscriptionTier` drive status/role constraints; many-to-many join tables (`user_teams`, `item_tags`, `item_assignees`) manage memberships and assignments.
- **Organization**: multi-tenant root with subscription caps, relationships to `User`, `Team`, `Item`, `APIKey`, `Webhook`, `UsageLog`, `UsageLog` and audit trails.
- **User/Team**: RBAC enabled via `User.role`, team membership via `user_teams`, creator/assignee links to items, activity logging, comments, attachments.
- **Item/Comment/Attachment**: Items support priority, status, subtasks, due/completion timestamps, tags, assignees, comments, attachments, activity logs; comments/attachments cascade on deletion.
- **Support models**: `Tag`, `APIKey`, `Webhook`, `UsageLog`, `ActivityLog` capture metadata, integrations, usage telemetry.

| Model | Key responsibilities |
| --- | --- |
| `Item` | Status/priority tracking, team/linking, subtasks, assignment, tagging, completion metadata |
| `APIKey` & `Webhook` | External integrations scoped to orgs, lifecycle and secret storage |
| `UsageLog` & `ActivityLog` | Observability: request metrics, user actions, entity changes |

## Service Layer
- **Organization/User/Team CRUD**: creation helpers ensure password hashing, activity logging, and membership management; team join adds users via secondary table.
- **Item lifecycle**: `create_item`, `update_item`, `delete_item` manage assignees/tags, enforce org scoping, auto-complete timestamps, and persist audit entries with change diffs; `get_items` also accepts `search_text` to search titles/descriptions alongside status, priority, and assignee filters.
- **Comments/Tags/API keys/Webhooks**: existence checks, scoped retrieval, and creation helper routines tied to organization context.
- **Observability & analytics**: `log_activity` centralizes audits; `get_activity_logs` filters by org/item; `get_item_analytics` aggregates counts by status/priority, overdue/completion metrics, avg completion time; `log_usage`/`get_usage_analytics` capture endpoint usage, average response, error rates.

## Source Files
- app/models.py
- app/services.py