# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require authentication via:
- **JWT Token:** `Authorization: Bearer <token>`
- **API Key:** `X-API-Key: <api_key>`

---

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization_id": 1
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

---

### Organizations

#### Create Organization
```http
POST /organizations
Content-Type: application/json

{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "subscription_tier": "professional"
}
```

#### Get Current Organization
```http
GET /organizations/current
Authorization: Bearer <token>
```

#### List Organization Users
```http
GET /organizations/{org_id}/users
Authorization: Bearer <token>
```

---

### Teams

#### Create Team (Admin)
```http
POST /teams
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Engineering",
  "description": "Product development team"
}
```

#### Add Team Member (Admin)
```http
POST /teams/{team_id}/members/{user_id}
Authorization: Bearer <token>
```

---

### Items

#### Create Item
```http
POST /items
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Implement feature X",
  "description": "Detailed description",
  "status": "todo",
  "priority": "high",
  "due_date": "2025-12-31T23:59:59",
  "estimated_hours": 8,
  "team_id": 1,
  "assignee_ids": [2, 3],
  "tag_ids": [1],
  "parent_item_id": null
}
```

#### Get Item
```http
GET /items/{item_id}
Authorization: Bearer <token>
```

#### List Items
```http
GET /items?team_id=1&status=in_progress&priority=high&assigned_to=2&skip=0&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `team_id` (optional): Filter by team
- `status` (optional): todo, in_progress, in_review, done, archived
- `priority` (optional): low, medium, high, urgent
- `assigned_to` (optional): User ID
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 100, max: 1000)

#### Update Item
```http
PUT /items/{item_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "done",
  "actual_hours": 6
}
```

#### Delete Item
```http
DELETE /items/{item_id}
Authorization: Bearer <token>
```

---

### Comments

#### Create Comment
```http
POST /comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "item_id": 1,
  "content": "This looks great!"
}
```

#### List Item Comments
```http
GET /items/{item_id}/comments
Authorization: Bearer <token>
```

---

### Tags

#### Create Tag
```http
POST /tags
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "bug",
  "color": "#EF4444"
}
```

#### List Tags
```http
GET /tags
Authorization: Bearer <token>
```

---

### API Keys

#### Create API Key (Admin)
```http
POST /api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Production Key",
  "expires_at": "2026-12-31T23:59:59"
}
```

#### List API Keys (Admin)
```http
GET /api-keys
Authorization: Bearer <token>
```

---

### Webhooks

#### Create Webhook (Admin)
```http
POST /webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": "item.created,item.updated,item.deleted",
  "secret": "webhook_secret_123"
}
```

#### List Webhooks (Admin)
```http
GET /webhooks
Authorization: Bearer <token>
```

---

### Activity Logs

#### List Activity Logs
```http
GET /activity?item_id=1&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `item_id` (optional): Filter by item
- `limit` (optional): Max results (default: 50, max: 500)

---

### Analytics

#### Item Analytics
```http
GET /analytics/items
Authorization: Bearer <token>
```

**Response:**
```json
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

#### Usage Analytics (Admin)
```http
GET /analytics/usage?days=30
Authorization: Bearer <token>
```

**Query Parameters:**
- `days` (optional): Days to analyze (default: 7, max: 90)

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions. Required role: admin"
}
```

### 404 Not Found
```json
{
  "detail": "Item not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Free tier:** 100 requests/minute
- **Starter:** 500 requests/minute
- **Professional:** 2,000 requests/minute
- **Enterprise:** Unlimited

---

## Webhooks

### Event Types
- `item.created`
- `item.updated`
- `item.deleted`
- `comment.created`
- `user.added`

### Payload Format
```json
{
  "event": "item.created",
  "timestamp": "2025-12-02T02:30:00Z",
  "organization_id": 1,
  "data": {
    "id": 123,
    "title": "New task",
    "status": "todo",
    "priority": "high"
  }
}
```

### Signature Verification
Webhooks include an `X-Signature` header with HMAC-SHA256 signature using your webhook secret.

---

*For interactive API documentation, visit `/docs`*
