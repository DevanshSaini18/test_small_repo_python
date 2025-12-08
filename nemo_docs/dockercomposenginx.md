## Docker Compose & NGINX

This project uses Docker Compose to orchestrate a three-service stack: PostgreSQL (db), the FastAPI application (app), and an NGINX reverse proxy (nginx). The composition centralizes networking, persistent storage, and environment-driven configuration for local development and simple production deployments.

Key components (see docker-compose.yml):

- db (Postgres 15-alpine)
  - Image: postgres:15-alpine
  - Environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - Persistent volume: postgres_data -> /var/lib/postgresql/data
  - Exposes port 5432 and includes a healthcheck (pg_isready) used by depends_on to gate app startup.

- app (FastAPI)
  - Built from the repository Dockerfile (build: .)
  - Exposes port 8000 to the host (8000:8000)
  - Environment variables wired for DATABASE_URL, SECRET_KEY, CORS_ORIGINS, DEBUG
  - Depends on db.service_healthy so the app waits for Postgres readiness
  - Mounts ./uploads into /app/uploads for file persistence
  - restart: unless-stopped policy

- nginx (nginx:alpine)
  - Acts as a fronting reverse proxy and TLS terminator
  - Host ports: 80 and 443 published
  - Mounts local nginx.conf into the container at /etc/nginx/nginx.conf (read-only) and an ./ssl directory into /etc/nginx/ssl for certificates
  - Depends on app and restarts unless-stopped

NGINX role and configuration (see docs/deployment.md and ./nginx.conf mapping in compose):

- NGINX is configured to accept HTTP (port 80) and HTTPS (port 443) and proxy application traffic to the app backend (typically to http://localhost:8000 inside the nginx container). The deployment docs include a sample server block showing:
  - HTTP -> HTTPS redirect
  - SSL certificate and key paths (e.g., /etc/letsencrypt/live/.../fullchain.pem and privkey.pem)
  - proxy_pass to the backend with typical proxy_set_header directives (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)

SSL + certificates
- Certificates are expected under ./ssl and are mounted read-only into the nginx container. The docs reference Certbot for obtaining Let’s Encrypt certificates and a sample TLS server configuration.

Operational notes in compose
- Service healthchecks and depends_on are used to order startup (db -> app -> nginx)
- Volumes: postgres_data (named volume) for DB persistence and host bind for uploads and SSL/nginx configuration
- Restart policy: services are configured to restart unless-stopped for resilience in simple deployments

Bringing the stack up
- Build and run with: docker-compose up -d (docker-compose.yml and Dockerfile used to build the app image)
- See docs/deployment.md for additional guidance on production TLS, load balancing, and cloud deployment patterns.

Relevant files:
- docker-compose.yml
- Dockerfile
- docs/deployment.md
- nginx.conf (mount referenced by compose)


## Source Files
- docker-compose.yml
- Dockerfile
- docs/deployment.md
- nginx.conf