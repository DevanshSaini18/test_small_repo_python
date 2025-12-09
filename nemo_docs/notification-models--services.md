# Notification Models & Services
- `app/notification_models.py` defines `Notification`/`NotificationPreference` tables with `NotificationType`/`NotificationPriority` enums, relationships back to users/items/comments, expiration, read flags, and digest/in-app/email toggles.
- `app/notification_schemas.py` supplies DTOs for creation, updates, bulk reads, stats summaries, and preference CRUD used throughout the routes and services.
- `app/notification_services.py` covers CRUD helpers, filters with expiration awareness, statistics per type/priority, preference creation/update, and trigger helpers (`notify_item_created`, `notify_item_updated`, `notify_item_completed`, `notify_comment_added`, etc.) that emit notifications when items or comments change while honoring user scopes and preference metadata.

## Source Files
- app/notification_models.py
- app/notification_schemas.py
- app/notification_services.py