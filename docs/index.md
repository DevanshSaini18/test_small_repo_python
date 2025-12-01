# Enterprise Todo Platform - Complete Documentation

## 🚀 Overview

A production-ready **10M ARR SaaS platform** built with FastAPI, featuring:

- ✅ **Multi-tenancy** (Organizations & Teams)
- 🔐 **Authentication & Authorization** (JWT + API Keys + RBAC)
- 📋 **Advanced Todo Management** (Priorities, Tags, Assignments, Due Dates, Subtasks)
- 💬 **Collaboration** (Comments, Activity Logs, Mentions)
- 📊 **Analytics & Reporting** (Item stats, Usage metrics)
- 🔗 **Webhooks & Integrations**
- 📈 **Usage Tracking & Rate Limiting**
- 🔍 **Audit Logs**

---

## 📦 Installation

```bash
# Install dependencies
poetry install

# Or with pip
pip install -r requirements.txt

# Run database migrations (tables created automatically)
# Database file: test.db (SQLite)
```

---

## 🏃 Running the Application

```bash
# Development mode
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🏗️ Architecture

### Database Schema

```
Organizations (Multi-tenant root)
├── Users (with roles: Owner, Admin, Member, Viewer)
├── Teams (group users)
├── Items (todos with advanced features)
│   ├── Tags (many-to-many)
│   ├── Assignees (many-to-many)
│   ├── Comments
│   ├── Attachments
│   └── Activity Logs
├── API Keys (for programmatic access)
├── Webhooks (event notifications)
└── Usage Logs (analytics)
```

### Subscription Tiers

| Tier | Max Users | Max Items | Features |
|------|-----------|-----------|----------|
| **Free** | 5 | 100 | Basic features |
| **Starter** | 20 | 1,000 | + Teams, Tags |
| **Professional** | 100 | 10,000 | + Webhooks, Analytics |
| **Enterprise** | Unlimited | Unlimited | + Custom integrations, SLA |

---

## 🔑 Authentication

### 1. JWT Authentication (User Login)

```bash
# Register a new user
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization_id": 1
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

# Use token in subsequent requests
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 2. API Key Authentication

```bash
# Create API key (Admin only)
POST /api/v1/api-keys
Authorization: Bearer <jwt_token>
{
  "name": "Production API Key",
  "expires_at": "2025-12-31T23:59:59"
}

# Use API key
X-API-Key: sk_abc123xyz...
```

---

## 📋 Core Features

### Organizations

```bash
# Create organization
POST /api/v1/organizations
{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "subscription_tier": "professional"
}

# Get current organization
GET /api/v1/organizations/current
Authorization: Bearer <token>
```

### Teams

```bash
# Create team (Admin only)
POST /api/v1/teams
{
  "name": "Engineering",
  "description": "Product development team"
}

# Add member to team
POST /api/v1/teams/{team_id}/members/{user_id}
```

### Items (Todos)

```bash
# Create item
POST /api/v1/items
{
  "title": "Implement user authentication",
  "description": "Add JWT-based auth system",
  "status": "todo",
  "priority": "high",
  "due_date": "2025-12-15T17:00:00",
  "estimated_hours": 8,
  "team_id": 1,
  "assignee_ids": [2, 3],
  "tag_ids": [1, 2],
  "parent_item_id": null
}

# List items with filters
GET /api/v1/items?status=in_progress&priority=high&team_id=1&assigned_to=2

# Update item
PUT /api/v1/items/{item_id}
{
  "status": "done",
  "actual_hours": 6
}

# Delete item
DELETE /api/v1/items/{item_id}
```

**Item Statuses:** `todo`, `in_progress`, `in_review`, `done`, `archived`

**Priority Levels:** `low`, `medium`, `high`, `urgent`

### Comments

```bash
# Add comment
POST /api/v1/comments
{
  "item_id": 1,
  "content": "Great progress! Let's review tomorrow."
}

# Get item comments
GET /api/v1/items/{item_id}/comments
```

### Tags

```bash
# Create tag
POST /api/v1/tags
{
  "name": "bug",
  "color": "#EF4444"
}

# List all tags
GET /api/v1/tags
```

---

## 📊 Analytics

### Item Analytics

```bash
GET /api/v1/analytics/items
Authorization: Bearer <token>

# Response
{
  "total_items": 150,
  "by_status": {
    "todo": 45,
    "in_progress": 30,
    "in_review": 15,
    "done": 55,
    "archived": 5
  },
  "by_priority": {
    "low": 20,
    "medium": 80,
    "high": 40,
    "urgent": 10
  },
  "overdue_items": 8,
  "completed_this_week": 12,
  "avg_completion_time_hours": 6.5
}
```

### Usage Analytics (Admin only)

```bash
GET /api/v1/analytics/usage?days=30
Authorization: Bearer <token>

# Response
{
  "total_requests": 15420,
  "requests_by_endpoint": {
    "/api/v1/items": 8500,
    "/api/v1/comments": 3200,
    "/api/v1/analytics/items": 450
  },
  "avg_response_time_ms": 45.2,
  "error_rate": 0.8
}
```

---

## 🔗 Webhooks

```bash
# Create webhook (Admin only)
POST /api/v1/webhooks
{
  "url": "https://your-app.com/webhook",
  "events": "item.created,item.updated,item.deleted",
  "secret": "your_webhook_secret"
}

# Webhook payload example
{
  "event": "item.created",
  "timestamp": "2025-12-02T02:30:00Z",
  "data": {
    "id": 123,
    "title": "New task",
    "organization_id": 1
  }
}
```

---

## 🔐 Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Owner** | Full access, billing, delete org |
| **Admin** | Manage users, teams, API keys, webhooks |
| **Member** | Create/edit items, comments |
| **Viewer** | Read-only access |

---

## 📝 Activity Logs

```bash
# Get activity logs
GET /api/v1/activity?item_id=1&limit=50

# Response
[
  {
    "id": 1,
    "action": "created",
    "entity_type": "item",
    "entity_id": 1,
    "user_id": 2,
    "details": null,
    "created_at": "2025-12-01T10:00:00Z"
  },
  {
    "id": 2,
    "action": "updated",
    "entity_type": "item",
    "entity_id": 1,
    "user_id": 3,
    "details": "{\"status\": {\"from\": \"todo\", \"to\": \"in_progress\"}}",
    "created_at": "2025-12-01T14:30:00Z"
  }
]
```

---

## 🚀 Production Deployment

### Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install poetry && poetry install --no-dev

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t todo-platform .
docker run -p 8000:8000 todo-platform
```

---

## 🧪 Testing

```bash
# Run tests (TODO: Add pytest)
pytest tests/

# Test coverage
pytest --cov=app tests/
```

---

## 📈 Monetization Strategy (10M ARR)

### Revenue Streams

1. **Subscription Plans** ($10-$99/month)
   - Free: 5 users, 100 items
   - Starter: $10/user/month
   - Professional: $25/user/month
   - Enterprise: Custom pricing

2. **Add-ons**
   - Advanced analytics: $50/month
   - Custom integrations: $100/month
   - Priority support: $200/month

3. **API Usage**
   - Free: 1,000 requests/month
   - Pay-as-you-go: $0.01/request

### Target Metrics

- **10,000 paying customers** @ $83/month average = **$10M ARR**
- **Conversion rate:** 5% free → paid
- **Churn rate:** <5% monthly
- **LTV/CAC ratio:** >3:1

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python 3.9+)
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **Authentication:** JWT (python-jose) + bcrypt
- **API Docs:** OpenAPI/Swagger
- **Deployment:** Docker, AWS/GCP/Azure

---

## 📞 Support

- **Documentation:** `/docs`
- **API Reference:** `/redoc`
- **Health Check:** `/health`
- **Status:** Operational ✅

---

*Built with ❤️ for enterprise productivity*
