## Troubleshooting & Maintenance

This guide consolidates diagnostic checks, maintenance tasks, and recovery commands for the Enterprise Todo Platform.

### Quick health checks
- API health: GET /health (returns status + timestamp). (main.py)
- Container health: Dockerfile defines a HEALTHCHECK calling /health; docker-compose defines a pg_isready healthcheck for Postgres. (Dockerfile, docker-compose.yml)

### Logs & error collection
- Application logs: stdout from Uvicorn (container logs). main.py configures logging and a global exception handler that returns 500 for unhandled errors — inspect container logs for stack traces. (main.py)
- Persisted logs: check host-mounted volumes or configured LOG_FILE (see .env.example) if file logging is enabled. (.env.example)
- External monitoring: docs recommend Sentry integration and log aggregation services for error/tracing. (docs/deployment.md)

### Common failure modes & diagnostics
- App won't start: inspect `docker logs todo_app` or `journalctl` if running systemd; check Dockerfile CMD (uvicorn main:app). Verify dependencies installed during image build. (Dockerfile)
- DB connection errors: confirm DATABASE_URL env var, container networking, and Postgres healthcheck (pg_isready). If using the default local SQLite in development, confirm file existence and permissions. (docker-compose.yml, app/database.py, .env.example)
- Migrations missing / schema mismatch: run Alembic migrations (alembic upgrade head) as documented in deployment guide. (docs/deployment.md)
- Long response times: review request timing logged by middleware (X-Process-Time header added by main.py) and examine DB query performance. (main.py)

### Recovery & common commands
- Recreate services: docker-compose down && docker-compose up -d --build (docker-compose.yml, Dockerfile)
- Tail logs: docker-compose logs -f app
- Run migrations: alembic upgrade head (docs/deployment.md)
- Manual DB check: docker exec -it todo_db pg_isready -U <user> or pg_dump for backups (docker-compose.yml, docs/deployment.md)

### Backups & restores
- Postgres backups: use pg_dump as shown in the deployment guide and schedule cron jobs for automated dumps. (docs/deployment.md)
- File uploads: ensure uploads volume is backed up (docker-compose mounts ./uploads). (.env.example, docker-compose.yml)

### Maintenance cadence
- Weekly: review error logs, disk usage, and DB connections.
- Monthly: apply OS and Python dependency security updates; run migrations in staging before production.
- Quarterly: performance tuning and backup restore drills. (docs/deployment.md)

Files referenced: main.py, app/database.py, docker-compose.yml, Dockerfile, .env.example, docs/deployment.md, docs/getting-started.md

## Source Files
- main.py
- app/database.py
- docker-compose.yml
- Dockerfile
- .env.example
- docs/deployment.md
- docs/getting-started.md