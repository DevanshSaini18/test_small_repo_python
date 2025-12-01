# Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Python 3.9+
- PostgreSQL (recommended for production)
- Redis (for caching - optional)
- Nginx (reverse proxy)
- SSL certificate

---

## 🐳 Docker Deployment

### 1. Build Docker Image

```bash
docker build -t enterprise-todo:latest .
```

### 2. Run with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: todo_platform
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://todo_user:secure_password@db/todo_platform
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

volumes:
  postgres_data:
```

```bash
docker-compose up -d
```

---

## ☁️ AWS Deployment

### Using AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 enterprise-todo

# Create environment
eb create production-env

# Deploy
eb deploy
```

### Using AWS ECS (Fargate)

1. Push image to ECR
2. Create ECS task definition
3. Create ECS service
4. Configure ALB
5. Set up RDS PostgreSQL

---

## 🌐 DigitalOcean App Platform

```yaml
# .do/app.yaml
name: enterprise-todo
services:
  - name: api
    github:
      repo: your-username/enterprise-todo
      branch: main
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8080
    envs:
      - key: DATABASE_URL
        value: ${db.DATABASE_URL}
      - key: SECRET_KEY
        value: ${SECRET_KEY}
    http_port: 8080

databases:
  - name: db
    engine: PG
    version: "15"
```

---

## 🔧 Environment Variables

Set these in production:

```bash
export DATABASE_URL="postgresql://user:pass@host/dbname"
export SECRET_KEY="$(openssl rand -hex 32)"
export CORS_ORIGINS="https://yourdomain.com"
export DEBUG=False
```

---

## 🔒 SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Monitoring & Logging

### Application Monitoring

```bash
# Install Sentry
pip install sentry-sdk[fastapi]
```

Add to `main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Log Aggregation

Use services like:
- **Datadog**
- **New Relic**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

---

## 🔄 Database Migrations

### Using Alembic

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

---

## 🚦 Health Checks

Configure health check endpoint:
```
GET /health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1701234567.89
}
```

---

## 📈 Scaling Strategies

### Horizontal Scaling
- Run multiple app instances behind load balancer
- Use session affinity if needed
- Share database across instances

### Vertical Scaling
- Increase CPU/RAM per instance
- Optimize database queries
- Add database read replicas

### Caching
```bash
# Add Redis for caching
pip install redis

# Cache frequently accessed data
# - User sessions
# - Analytics data
# - API responses
```

---

## 🔐 Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Set strong SECRET_KEY
- [ ] Enable CORS only for trusted origins
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Database backups
- [ ] Input validation
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection
- [ ] CSRF protection

---

## 💾 Backup Strategy

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U todo_user -d todo_platform > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * /usr/bin/pg_dump -U todo_user todo_platform > /backups/backup_$(date +\%Y\%m\%d).sql
```

### File Backups
- Upload directory
- Configuration files
- SSL certificates

---

## 📞 Support & Maintenance

### Monitoring Checklist
- [ ] API response times
- [ ] Error rates
- [ ] Database connections
- [ ] Disk space
- [ ] Memory usage
- [ ] CPU usage

### Regular Tasks
- Weekly: Review error logs
- Monthly: Security updates
- Quarterly: Performance optimization
- Yearly: Architecture review

---

*For questions, contact: support@yourdomain.com*
