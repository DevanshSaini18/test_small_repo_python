# Export Service & Reports

app/export.py implements the ExportService used by API export/report endpoints to stream data across CSV, JSON, and report payloads.

Highlights:
- export_items_to_csv and export_items_to_json reuse get_items, serialize item metadata plus assignees/tags, optionally include comments, and surface timestamps or nested creator info.
- generate_team_report and generate_user_report aggregate status/priority breakdowns, workload, completion rates, and recent ActivityLog entries for team/user contextual summaries, returning errors when targets are missing.


## Source Files
- app/export.py