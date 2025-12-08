# Export Service (Reports & Data Exports)

app/export.py defines ExportService, which produces CSV/JSON exports and summary reports consumed by the export and report endpoints described above. The service uses get_items/get_item_analytics to pull org-scoped item data (with skip=0 and limit=10000 safeguards) and serializes related assignees, tags, created_by, and optional comments via the csv and json stdlib helpers.

Capabilities include:
- export_items_to_csv: writes item metadata (status, priority, timestamps, estimates) to a StringIO-backed CSV with flattened assignee/tag lists, suitable for streaming responses.
- export_items_to_json: builds rich JSON payloads with nested assignees, tags, created_by info, and optional comments, along with export_date and organization metadata.
- generate_team_report / generate_user_report: compute statistics (completion rates, status/priority breakdowns, overdue counts, member workload, recent activity) for teams and users by querying Team, Item, User, ActivityLog, and aggregating using defaultdict-based counters.

Why it matters:
This isolated export service keeps serialization concerns out of the route handlers while ensuring the exported artifact mirrors the core domain model and logged analytics. Reports incorporate calculated insights, so clients have a single place to adjust summaries without touching endpoints.

## Source Files
- app/export.py