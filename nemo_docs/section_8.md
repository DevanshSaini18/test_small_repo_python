# Infrastructure & Deployment Notes

The repository contains Docker and deployment artifacts and supporting docs to run the application in development and production.

Key files & responsibilities:
- docker-compose.yml: orchestration for PostgreSQL (production or dev), application, and Nginx reverse proxy. Configures volumes, health checks, environment variables, ports, and restart policies.
- Dockerfile: builds a Python 3.11-slim based image (installs system deps, Python deps, copies source, runs uvicorn). Use for containerized deployment.
- .env.example: template for environment variables (DB URL, SECRET_KEY, CORS, rate limiting, upload paths, logging). Important to fill for production and not keep secrets in source.
- docs/deployment.md & docs/feature-comparison.md: provide production deployment guidance — SSL termination, scaling notes, monitoring, backups, migrations, and security hardening recommendations.

Production considerations:
- Replace SQLite with managed Postgres & add Alembic migrations (no migrations implemented currently).
- Move SECRET_KEY and other secrets to environment / secret manager; do not use runtime-generated secrets in production.
- Configure CORS, rate limits, and RBAC defaults appropriately; enable request/usage logging into UsageLog for billing/analytics.
- Add CI pipeline to build images, run tests, run migrations, and push artifacts. Add monitoring/alerting (Prometheus/Grafana, centralized logs) per docs.


## Source Files
- docker-compose.yml
- Dockerfile
- .env.example
- docs/deployment.md
- README.md