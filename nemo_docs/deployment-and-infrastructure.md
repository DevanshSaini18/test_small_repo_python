# Deployment and Infrastructure
## Container image & runtime
- Base image is `python:3.11-slim`; installs GCC and PostgreSQL client, installs dependencies via Poetry (falls back to `requirements.txt`), copies source, creates `uploads/`, exposes port 8000, and defines a health check against `/health` before launching `uvicorn main:app`. (Dockerfile)

## Compose deployment stack
- `docker-compose.yml` orchestrates three services: a Postgres 15 Alpine database with persistent `postgres_data` volume and `pg_isready` health check; the app build that injects `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `DEBUG`, mounts `uploads`, waits for the healthy DB, and restarts unless stopped; and an Nginx reverse proxy that exposes 80/443, mounts the local `nginx.conf`/`ssl` directories, and depends on the app. (docker-compose.yml)

## Environment & secrets
- `.env.example` documents runtime configuration: database string (SQLite default vs. PostgreSQL), secret key guidance, JWT algorithm/expiry, CORS origins, app metadata, debug flag, rate limits, optional SMTP entries, webhook timeouts/retries, upload constraints, and logging level/file—serving as the reference for production overrides. (.env.example)

## Production deployment & operations
- `docs/deployment.md` consolidates infrastructure advice: Docker image/Compose commands, AWS Elastic Beanstalk/ECS and DigitalOcean App Platform flows, certbot/Nginx TLS snippets, Sentry integration, log aggregation targets, Alembic migrations, health-check payload, horizontal/vertical scaling tactics, Redis caching, backup scripts (Postgres dump + uploads/configs), and ongoing monitoring/security/maintenance checklists. (docs/deployment.md)

## Source Files
- Dockerfile
- docker-compose.yml
- .env.example
- docs/deployment.md