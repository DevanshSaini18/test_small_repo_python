# Application Entrypoint, Middleware & Observability

main.py is the FastAPI application bootstrap that configures middleware, logging, global exception handling, DB creation and mounts the API router.

Middleware & behaviors:
- CORS: CORSMiddleware is configured with allow_origins=["*"] (placeholder) — update to explicit origins in production.
- Request timing: a custom middleware wraps each request to record processing time (ms), logs method/path/status/time and injects X-Process-Time header into responses.
- Global exception handler: catches unhandled exceptions, logs stack traces, and returns a 500 JSON response.
- Auto schema/docs: FastAPI docs available at /docs and /redoc per app config. Note: the docs will reflect recent route changes (see "List items" below).

Operational observability & logging:
- Uses Python logging with INFO level; request middleware logs each request. Services and handlers raise HTTPException with clear status codes which surface to clients.
- The code contains TODOs to persist request-level metrics to the DB (log_usage) where the org_id extraction would be required from the auth token (or from the Organization dependency used in routes).

Startup behavior:
- Calls Base.metadata.create_all(bind=engine) to ensure DB tables exist at service start.
- Includes root and /health endpoints for basic readiness/liveness checks.

API note — List items / text search changes:
- The list items endpoint no longer accepts a free-text "search" query parameter. The route signature and the service function were updated to remove the text-search parameter and the corresponding filtering logic.
- Current supported filters include team_id, status, priority, assigned_to as well as pagination (skip, limit). The Organization dependency is injected into the route and the service is called with org.id to scope results.
- Because text search was removed from the service (get_items) and the route, clients that relied on "search" must switch to available filters or reintroduce search in a future change. The OpenAPI schema/docs served at /docs will reflect this removal.

## Source Files
- main.py
- app/routes.py
- app/services.py