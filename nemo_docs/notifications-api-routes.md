# Notifications API Routes
- `app/notification_routes.py` registers the `/notifications` router guarded by `get_current_active_user`, letting admins/owners (or self) create notifications and letting users list/filter (read/type/priority/pagination), fetch unread batches, inspect stats, retrieve individual notifications, mark them read (single/bulk/all), delete entries, and manage preference records.
- Preference endpoints (`/preferences/me`) surface `NotificationPreferenceRead`/`NotificationPreferenceUpdate` payloads so clients can toggle digest/in-app/email settings tied to the current user.

## Source Files
- app/notification_routes.py