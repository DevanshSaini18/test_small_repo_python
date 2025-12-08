# Notification Service

app/notifications.py provides NotificationService helpers used by export/report/alert routes to keep users informed about assignments, comments, status changes, and upcoming due dates.

Highlights:
- send_email logs (placeholder for SMTP) and supports plain/text + optional HTML bodies while capturing failures.
- notify_item_assigned, notify_comment_added, and notify_status_changed build contextual subjects/bodies for assignees and honor HTML formatting.
- send_due_date_reminders queries Org items due in a given window, filters out completed work, and attempts to notify assignees while returning summary stats (total items, notifications, successes).


## Source Files
- app/notifications.py