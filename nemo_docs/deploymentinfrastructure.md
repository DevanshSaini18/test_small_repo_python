## Deployment & Infrastructure

This project is packaged for containerized deployments and includes curated guidance and artifacts for local, Docker Compose, and cloud-hosted deployments.

Key components
- Dockerfile: production image based on python:3.11-slim; installs system deps, application dependencies (Poetry/pip fallback), copies source, exposes port 8000, creates uploads directory and defines a HEALTHCHECK against /health.
- docker-compose.yml: multi-service composition for local/dev stacks with PostgreSQL (postgres:15-alpine), app service (builds from Dockerfile), and an Nginx reverse proxy. Declares a postgres_data volume and mounts ./uploads into the app container.
- .env.example: canonical environment variables (DATABASE_URL, SECRET_KEY, CORS_ORIGINS, DEBUG, rate limits, webhook/file settings, logging). Use these for runtime configuration.
- docs/deployment.md: authoritative deployment instructions covering Docker Compose, AWS (Elastic Beanstalk, ECS/Fargate), DigitalOcean App Platform, SSL/TLS (Let's Encrypt + Certbot + Nginx config example), monitoring (Sentry snippet), Alembic migrations, health checks, scaling strategies, caching recommendations, backups, and maintenance checklist.
- main.py: application entrypoint exposing /health and root endpoints, registering API router, creating DB schema via SQLAlchemy Base.metadata.create_all(bind=engine), and adding request-timing middleware. The /health endpoint is used by container health checks and orchestrators.

Deployment options (summary)
- Docker Compose (local/dev): docker-compose.yml orchestrates db, app, and nginx. Exposes ports 5432 (db) and 8000 (app) and mounts uploads and ssl/nginx config files.
- Docker image: build with Dockerfile (docker build -t enterprise-todo:latest .). Image includes a HEALTHCHECK that calls the app /health endpoint.
- Cloud platforms: docs include patterns for Elastic Beanstalk, ECS/Fargate (ECR, task definitions, ALB), and DigitalOcean App Platform (app.yaml example).

Operational considerations documented
- Environment variables: production secrets (SECRET_KEY, DATABASE_URL, CORS_ORIGINS, DEBUG) are surfaced in .env.example and referenced in compose/docs.
- SSL/TLS: Nginx configuration for HTTP->HTTPS redirect and proxying to the app on port 8000; Let's Encrypt certbot commands are documented.
- Health checks & monitoring: /health endpoint; Sentry integration snippet is provided in docs and recommended to be initialized in main.py.
- Migrations & backups: Alembic migration workflow and PostgreSQL pg_dump examples for scheduled backups are included in docs/deployment.md.
- Scaling & caching: horizontal scaling recommendations, use of load balancers, and Redis for caching are described.

Files
- docker-compose.yml
- Dockerfile
- docs/deployment.md
- .env.example
- main.py
- README.md

## Source Files
- docker-compose.yml
- Dockerfile
- docs/deployment.md
- .env.example
- main.py
- README.md