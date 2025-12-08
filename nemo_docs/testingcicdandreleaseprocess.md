## Testing, CI/CD, and Release Process

This project includes the pieces needed for a standard test→build→release pipeline using Poetry/pip for dependency management, Docker for packaging, and Docker Compose / cloud services for deployment. The following summarizes the concrete commands and artifacts present in the repository and a recommended linear flow that maps to CI/CD stages.

### Key artifacts
- Dependency & metadata: pyproject.toml (package name, version) and requirements.txt (pins used for pip workflows). (.python-version pins toolchain)
- Test invocation (documented): pytest tests/ (coverage via pytest --cov)
- Container build: Dockerfile (builds python:3.11-slim image, installs dependencies via Poetry or fallback to requirements.txt, exposes 8000, includes HEALTHCHECK)
- Local orchestration: docker-compose.yml (Postgres, app, nginx with healthcheck dependencies)
- Deployment guidance: docs/deployment.md (Docker, Docker Compose, AWS EB/ECS ECR steps, DigitalOcean app spec)
- Runtime health endpoint & global handlers: main.py (GET /health, logging middleware, DB bootstrap via SQLAlchemy Base.metadata.create_all)

### Test stage (CI job)
- Install environment: use Poetry (pyproject.toml) or pip install -r requirements.txt depending on chosen runner image.
- Run unit/integration tests: pytest tests/ (include --cov to collect coverage). Exit non-zero on failures.
- Optional static checks: linters/formatters are not included but can be added by invoking black/ruff/mypy in the same stage.

Example commands
- poetry install --no-dev && pytest tests/ --cov
- pip install -r requirements.txt && pytest tests/ --cov

### Build stage (CI job)
- Build Docker image using Dockerfile: docker build -t enterprise-todo:${GIT_TAG:-latest} .
- Run container locally or in CI to smoke-test health: docker run -p 8000:8000 ...; or rely on the Dockerfile HEALTHCHECK which probes /health (Dockerfile uses a python requests call).

### Release & deploy stage (CI job)
- Tagging: use repository tag (semantic version from pyproject.toml can be synced to Git tag) and use that tag for image: e.g., enterprise-todo:2.0.0
- Push image to registry (ECR, Docker Hub, or private registry) as described in docs/deployment.md (ECR push steps are outlined there).
- Run DB migrations before/after deploy: Alembic commands are listed in docs/deployment.md (alembic revision --autogenerate; alembic upgrade head).
- Deploy: options shown in docs/deployment.md include docker-compose up -d, AWS Elastic Beanstalk (eb deploy), ECS (push to ECR and register task/service), or DigitalOcean App Platform (app.yaml).

### Runtime checks and observability
- Health checks: main.py exposes GET /health; Dockerfile includes a HEALTHCHECK that queries this endpoint.
- Logging: main.py configures request logging and a global exception handler; these integrate into CI/CD smoke tests and orchestrator health checks.

Source files: the CI/CD flow maps to these repository files for commands, image build, health checks, and deployment notes.

## Source Files
- docs/deployment.md
- README.md
- pyproject.toml
- Dockerfile
- docker-compose.yml
- requirements.txt
- main.py
- .python-version