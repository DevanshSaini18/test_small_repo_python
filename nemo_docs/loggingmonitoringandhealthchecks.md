## Logging, Monitoring, and Health Checks

This project implements application-level logging, basic request monitoring, and container health checks to support operational visibility.

### Logging

- Initialization: logging is configured in main.py via logging.basicConfig(level=logging.INFO) and a module logger is created (logger = logging.getLogger(__name__)). (main.py)
- Request logs: an HTTP middleware logs every request with method, path, response status and processing time. The middleware also injects an X-Process-Time header (milliseconds) into responses for latency inspection. The middleware block is in main.py and outputs lines like: "GET /api/v1/items - Status: 200 - Time: 12ms". (main.py)
- Error logging: a global exception handler catches unhandled exceptions, logs them with stack traces (logger.error(..., exc_info=True)) and returns a standardized 500 response. This centralizes unexpected error visibility. (main.py)
- Configuration: runtime logging settings can be adjusted through environment variables in .env.example (LOG_LEVEL, LOG_FILE) and the app uses the SECRET_KEY/DEBUG vars also present there. ( .env.example )
- Operational note in code: middleware includes a TODO to forward usage/analytics to the database (commented in main.py), indicating where request/usage logging could be persisted for analytics. (main.py)

### Request Timing and Metrics

- X-Process-Time header: every HTTP response is augmented with X-Process-Time (ms), enabling quick latency checks from clients or synthetic monitors. (main.py)
- Middleware-level logging provides per-request timing that can be scraped or forwarded to a logging/metrics pipeline for aggregation (middleware in main.py). (main.py)

### Health Checks (Application & Containers)

- Application health endpoint: GET /health returns a small JSON payload with status and timestamp: {"status": "healthy", "timestamp": <float>}. This endpoint is used by container-level checks and external probes. (main.py)
- Dockerfile HEALTHCHECK: the Docker image defines a HEALTHCHECK that runs a small Python request against http://localhost:8000/health at regular intervals to mark container liveness. This is defined in Dockerfile and attempts to verify the app is serving the health endpoint. (Dockerfile)
- Compose-level healthchecks and ordering: docker-compose.yml configures a postgres service healthcheck using pg_isready and sets the app service to depend on the db service with condition: service_healthy. This ensures the app container waits for a healthy DB before starting dependent operations. (docker-compose.yml)

### Runtime / Container Logging

- Uvicorn: the container command starts uvicorn with log_level="info" (Dockerfile CMD), so Uvicorn access/error logs will be emitted to stdout/stderr and captured by container log drivers. (Dockerfile)
- Compose ports and volumes: docker-compose.yml exposes application and database ports and mounts uploads; container logging should therefore be collected via the platform's logging driver or sidecar. (docker-compose.yml)

Source files:
- main.py
- docker-compose.yml
- Dockerfile
- .env.example

## Source Files
- main.py
- docker-compose.yml
- Dockerfile
- .env.example