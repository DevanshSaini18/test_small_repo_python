# Notification Service (Email Alerts & Reminders)

app/notifications.py provides NotificationService, which currently logs email delivery flows for item assignments, comments, status changes, and due-date reminders in place of a fully configured SMTP client.

Capabilities include:
- send_email: composes multipart plain/text+HTML MIME messages, logs deliveries, and is prepared to use SMTP hosts (default smtp.gmail.com) once enabled.
- notify_item_assigned / notify_comment_added / notify_status_changed: iterate assignees (excluding the commenter where appropriate) and send templated notifications detailing titles, descriptions, priority, status, and due dates; each returns per-recipient success statuses.
- send_due_date_reminders: finds items due on a target date (days_before) with non-DONE status, notifies each assignee with a reminder template, and returns aggregated statistics (total_items, notifications sent, successes).

Why it matters:
Centralizing notification templates and delivery tracking keeps the reminder and alert endpoints lean, while the same service can later be extended with real SMTP credentials, queueing, or integration with third-party email providers.

## Source Files
- app/notifications.py