# Application Entrypoint, Middleware & Observability

main.py is the FastAPI application bootstrap that configures middleware, logging, global exception handling, DB creation and mounts the API router.

Middleware & behaviors:
- CORS: CORSMiddleware is configured with allow_origins=["*"] (placeholder) — update to explicit origins in production.
- Request timing: a custom middleware wraps each request to record processing time (ms), logs method/path/status/time and injects X-Process-Time header into responses.
- Global exception handler: catches unhandled exceptions, logs stack traces, and returns a 500 JSON response.
- Auto schema/docs: FastAPI docs available at /docs and /redoc per app config.

Operational observability & logging:
- Uses Python logging with INFO level; request middleware logs each request. Services and handlers also raise HTTPException with clear status codes which surface to clients.
- The code contains TODOs to persist request-level metrics to the DB (log_usage) where the org_id extraction would be required from the auth token.

Startup behavior:
- Calls Base.metadata.create_all(bind=engine) to ensure DB tables exist at service start.
- Includes root and /health endpoints for basic readiness/liveness checks.

Notes on recent route/service updates:
- Search filtering has been removed from the items listing endpoint and service layer, so list_items now focuses on team, status, priority, and assignee filters only.

## Source Files
- main.py
- app/routes.py
- app/services.py