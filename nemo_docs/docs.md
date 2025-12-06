# Architecture Documentation

This document provides a comprehensive architectural overview of the *Enterprise Todo Platform* - a production-ready SaaS application built with FastAPI, designed for multi-tenancy, scalability, and enterprise-grade features.

---

<!-- START: High-Level System Overview -->
## 2.1 High-Level System Overview

*Linked Files:*
- main.py
- app/__init__.py
- app/database.py
- docker-compose.yml
- Dockerfile
- requirements.txt

### System Architecture

The Enterprise Todo Platform follows a *layered architecture* pattern with clear separation of concerns:

*Architecture Layers:*
1. *Client Applications* - Web, Mobile, Third-party Integrations
2. *API Gateway Layer* - CORS Middleware, Request Timing Middleware, Logging Handler
3. *Authentication Layer* - JWT Auth, API Keys, RBAC
4. *Routes Layer* - FastAPI Endpoints (API Controllers)
5. *Business Logic Layer* - Services Module (CRUD Operations, Validation, Business Rules)
6. *Data Access Layer* - SQLAlchemy ORM Models (Models, Relationships, Database Sessions)
7. *Database Layer* - SQLite / PostgreSQL

### Key Architectural Principles

1. *Multi-Tenancy*: Organization-based data isolation with subscription tiers
2. *Separation of Concerns*: Clear boundaries between layers (routes, services, models)
3. *Dependency Injection*: FastAPI's dependency system for authentication and database sessions
4. *RESTful Design*: Resource-oriented API endpoints following REST principles
5. *Security First*: JWT authentication, RBAC, password hashing, API key management
6. *Scalability*: Stateless design, database connection pooling, async-ready
7. *Observability*: Request logging, activity tracking, usage analytics

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| *Framework* | FastAPI 0.104+ | High-performance async web framework |
| *ORM* | SQLAlchemy 2.0 | Database abstraction and models |
| *Database* | SQLite/PostgreSQL | Data persistence |
| *Authentication* | JWT (python-jose) | Token-based authentication |
| *Password Hashing* | bcrypt (passlib) | Secure password storage |
| *Validation* | Pydantic 2.5+ | Request/response validation |
| *Documentation* | OpenAPI/Swagger | Auto-generated API docs |
| *Deployment* | Docker, Uvicorn | Containerization and ASGI server |

<!-- END: High-Level System Overview -->

---

<!-- START: Services and Components -->
## 2.2 Services and Components

### Core Components

The application is organized into the following modules:

<!-- START: Application Entry Point -->
#### 1. *main.py* - Application Entry Point

*Linked Files:*
- main.py

The main application file that initializes the FastAPI app and configures middleware.

*Key Responsibilities:*
- FastAPI application initialization
- CORS middleware configuration
- Request timing and logging middleware
- Global exception handling
- Database table creation
- Router registration
- Health check endpoints

*Middleware Stack:*
1. CORS Middleware (Cross-Origin Resource Sharing)
2. Request Timing Middleware (Logs all requests + timing)
3. Global Exception Handler (Catches unhandled errors)

*Endpoints:*
- GET / - Root endpoint with API information
- GET /health - Health check endpoint
- /api/v1/* - All API routes (via router)

<!-- END: Application Entry Point -->

---

<!-- START: Database Configuration -->
#### 2. *app/database.py* - Database Configuration

*Linked Files:*
- app/database.py

Manages database connections and session lifecycle.

*Key Components:*
- engine - SQLAlchemy database engine (SQLite with thread-safe configuration)
- SessionLocal - Session factory for creating database sessions
- Base - Declarative base for ORM models
- get_db() - Dependency function that yields database sessions

*Database Configuration:*
python
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# Production: postgresql://user:password@host/database


<!-- END: Database Configuration -->

---

<!-- START: Data Models -->
#### 3. *app/models.py* - Data Models (ORM)

*Linked Files:*
- app/models.py

Defines the database schema using SQLAlchemy ORM models.

*Entity Relationships:*
- *Organization* (1:N) → Users, Teams, Items, APIKeys, Webhooks, UsageLogs
- *Users* (N:M) ↔ Teams
- *Items* (N:M) ↔ Users (assignees), Tags
- *Items* (1:N) → Comments, Attachments, ActivityLogs

*Core Models:*

1. *Organization* - Top-level tenant entity
   - Fields: name, slug, subscription_tier, is_active, max_users, max_items
   - Relationships: users, teams, items, api_keys, webhooks, usage_logs

2. *User* - User accounts within organizations
   - Fields: email, username, full_name, hashed_password, role, is_active
   - Relationships: organization, teams (N:M), created_items, assigned_items (N:M), comments, activity_logs
   - Roles: OWNER, ADMIN, MEMBER, VIEWER

3. *Team* - Collaborative groups within organizations
   - Fields: name, description, organization_id
   - Relationships: organization, members (N:M via user_teams), items

4. *Item* - Core todo/task entity
   - Fields: title, description, status, priority, due_date, estimated_hours, actual_hours, completed_at
   - Relationships: organization, team, assignees (N:M), tags (N:M), comments, attachments, activity_logs, parent_item, subtasks
   - Status: TODO, IN_PROGRESS, IN_REVIEW, DONE, ARCHIVED
   - Priority: LOW, MEDIUM, HIGH, URGENT

5. *Comment* - Comments on items
   - Fields: content, item_id, author_id
   - Relationships: item, author

6. *Tag* - Categorization labels
   - Fields: name, color
   - Relationships: items (N:M via item_tags)

7. *Attachment* - File attachments on items
   - Fields: filename, file_path, file_size, mime_type
   - Relationships: item, uploaded_by

8. *ActivityLog* - Audit trail for all actions
   - Fields: action, entity_type, entity_id, user_id, item_id, details
   - Relationships: user, item

9. *APIKey* - API keys for programmatic access
   - Fields: key, name, organization_id, is_active, expires_at, last_used_at
   - Relationships: organization

10. *Webhook* - Event-driven integrations
    - Fields: url, events (JSON array), secret, is_active
    - Relationships: organization

11. *UsageLog* - API usage tracking
    - Fields: organization_id, endpoint, method, status_code, response_time_ms
    - Relationships: organization

<!-- END: Data Models -->

---

<!-- START: Pydantic Schemas -->
#### 4. *app/schemas.py* - Pydantic Schemas

*Linked Files:*
- app/schemas.py

Defines request/response validation schemas using Pydantic.

*Schema Categories:*
- *Create Schemas*: For POST requests (e.g., UserCreate, ItemCreate)
- *Update Schemas*: For PUT/PATCH requests (e.g., ItemUpdate)
- *Response Schemas*: For API responses (e.g., UserResponse, ItemResponse)
- *Login/Auth Schemas*: For authentication (e.g., UserLogin, Token)

*Key Features:*
- Automatic validation of incoming data
- Type safety and IDE autocomplete
- Serialization/deserialization
- Documentation generation

<!-- END: Pydantic Schemas -->

---

<!-- START: Authentication Utilities -->
#### 5. *app/auth.py* - Authentication Utilities

*Linked Files:*
- app/auth.py

Provides authentication and security utilities.

*Key Functions:*

1. *Password Management:*
   - get_password_hash(password) - Hash passwords using bcrypt
   - verify_password(plain, hashed) - Verify password against hash

2. *JWT Token Management:*
   - create_access_token(data, expires_delta) - Generate JWT tokens
   - decode_access_token(token) - Decode and verify JWT tokens
   - Token expiration: 24 hours (configurable)
   - Algorithm: HS256

3. *API Key Generation:*
   - generate_api_key() - Generate secure API keys with sk_ prefix

*Security Configuration:*
python
SECRET_KEY = secrets.token_urlsafe(32)  # Production: use env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


<!-- END: Authentication Utilities -->

---

<!-- START: FastAPI Dependencies -->
#### 6. *app/dependencies.py* - FastAPI Dependencies

*Linked Files:*
- app/dependencies.py
- app/auth.py
- app/models.py

Implements dependency injection for authentication and authorization.

*Key Dependencies:*

1. **get_current_user(credentials, db)**
   - Extracts and validates JWT token from Authorization header
   - Returns authenticated User object
   - Updates last_login timestamp

2. **get_current_active_user(current_user)**
   - Ensures user is active
   - Used as dependency in most endpoints

3. **get_current_organization(current_user, db)**
   - Retrieves user's organization
   - Validates organization is active
   - Enforces multi-tenancy

4. **require_role(required_role)**
   - Factory function for role-based access control
   - Implements role hierarchy: VIEWER < MEMBER < ADMIN < OWNER
   - Returns 403 if user lacks required role

5. **verify_api_key(x_api_key, db)**
   - Validates API key from X-API-Key header
   - Checks expiration and active status
   - Returns associated organization
   - Updates last_used_at timestamp

*Role Hierarchy:*
- *OWNER (3)* - Full control, billing, user management
- *ADMIN (2)* - Create teams, manage API keys, webhooks
- *MEMBER (1)* - Create/edit items, comments
- *VIEWER (0)* - Read-only access

<!-- END: FastAPI Dependencies -->

---

<!-- START: Business Logic Layer -->
#### 7. *app/services.py* - Business Logic Layer

*Linked Files:*
- app/services.py
- app/models.py
- app/schemas.py
- app/auth.py

Contains all business logic and CRUD operations.

*Service Modules:*

1. *Organization Services*
   - create_organization(db, org) - Create new organization
   - get_organization(db, org_id) - Retrieve organization by ID

2. *User Services*
   - create_user(db, user) - Create user with hashed password
   - get_user_by_email(db, email) - Find user by email
   - get_users_by_organization(db, org_id) - List org users

3. *Team Services*
   - create_team(db, team, org_id, user) - Create team
   - add_user_to_team(db, team_id, user_id) - Add team member

4. *Item Services* (Most comprehensive)
   - create_item(db, item, org_id, user) - Create item with assignees/tags
   - get_item(db, item_id, org_id) - Retrieve single item
   - get_items(db, org_id, filters...) - List items with filtering
   - update_item(db, item_id, item_update, org_id, user) - Update with change tracking
   - delete_item(db, item_id, org_id, user) - Delete item

5. *Comment Services*
   - create_comment(db, comment, user, org_id) - Add comment to item
   - get_comments_by_item(db, item_id, org_id) - List item comments

6. *Tag Services*
   - create_tag(db, tag) - Create new tag
   - get_tags(db) - List all tags

7. *API Key Services*
   - create_api_key(db, api_key_data, org_id) - Generate API key
   - get_api_keys(db, org_id) - List organization API keys

8. *Webhook Services*
   - create_webhook(db, webhook, org_id) - Register webhook
   - get_webhooks(db, org_id) - List organization webhooks

9. *Activity Log Services*
   - log_activity(db, action, entity_type, entity_id, ...) - Log audit events
   - get_activity_logs(db, org_id, item_id, limit) - Retrieve activity logs

10. *Analytics Services*
    - get_item_analytics(db, org_id) - Item statistics (by status, priority, overdue, etc.)
    - log_usage(db, org_id, endpoint, method, status_code, response_time_ms) - Log API usage
    - get_usage_analytics(db, org_id, days) - Usage statistics (requests, response times, error rates)

*Key Features:*
- Organization-scoped operations (multi-tenancy)
- Automatic activity logging for audit trails
- Change tracking for updates
- Relationship management (assignees, tags)
- Business rule enforcement (e.g., auto-complete timestamp)

<!-- END: Business Logic Layer -->

---

<!-- START: API Endpoints -->
#### 8. *app/routes.py* - API Endpoints

*Linked Files:*
- app/routes.py
- app/services.py
- app/schemas.py
- app/dependencies.py
- app/models.py

Defines all REST API endpoints using FastAPI routers.

*Endpoint Categories:*

1. *Authentication Routes* (/auth)
   - POST /auth/register - Register new user
   - POST /auth/login - Login and get JWT token
   - GET /auth/me - Get current user info

2. *Organization Routes* (/organizations)
   - POST /organizations - Create organization
   - GET /organizations/me - Get current organization
   - GET /organizations/{org_id}/users - List organization users

3. *Team Routes* (/teams)
   - POST /teams - Create team (Admin only)
   - POST /teams/{team_id}/members/{user_id} - Add team member (Admin only)

4. *Item Routes* (/items)
   - POST /items - Create item
   - GET /items/{item_id} - Get item by ID
   - GET /items - List items with filters (status, priority, assignee, team)
   - PUT /items/{item_id} - Update item
   - DELETE /items/{item_id} - Delete item

5. *Comment Routes* (/comments)
   - POST /comments - Create comment on item
   - GET /items/{item_id}/comments - List item comments

6. *Tag Routes* (/tags)
   - POST /tags - Create tag
   - GET /tags - List all tags

7. *API Key Routes* (/api-keys)
   - POST /api-keys - Create API key (Admin only)
   - GET /api-keys - List API keys (Admin only)

8. *Webhook Routes* (/webhooks)
   - POST /webhooks - Create webhook (Admin only)
   - GET /webhooks - List webhooks (Admin only)

9. *Activity Log Routes* (/activity)
   - GET /activity - Get activity logs
   - GET /items/{item_id}/activity - Get item-specific activity

10. *Analytics Routes* (/analytics)
    - GET /analytics/items - Get item analytics
    - GET /analytics/usage - Get usage analytics (Admin only)

*Common Patterns:*
- All endpoints use dependency injection for auth/db
- Organization scoping enforced via get_current_organization
- Role-based access control via require_role
- Consistent error handling (404, 403, 401)
- Query parameters for filtering and pagination

<!-- END: API Endpoints -->

<!-- END: Services and Components -->

---

<!-- START: Data Flow -->
## 2.3 Data Flow

*Linked Files:*
- app/routes.py
- app/services.py
- app/dependencies.py
- app/auth.py
- app/models.py

### 1. User Authentication Flow

*Linked Files:*
- app/routes.py (login endpoint)
- app/auth.py (JWT creation, password verification)
- app/dependencies.py (token validation)
- app/models.py (User model)

*Steps:*
1. Client sends POST request to /api/v1/auth/login with email and password
2. Server validates request using Pydantic schemas
3. Server queries database for user by email
4. Server verifies password using bcrypt
5. Server creates JWT token with user ID
6. Server returns access token to client
7. Client includes token in subsequent requests via Authorization header
8. Server decodes JWT token and retrieves user from database
9. Server returns protected resources

---

### 2. Item Creation Flow

*Linked Files:*
- app/routes.py (create_new_item endpoint)
- app/services.py (create_item function)
- app/dependencies.py (authentication dependencies)
- app/models.py (Item, User, Tag models)

*Steps:*
1. Client sends POST request to /items with JWT token
2. Routes layer verifies JWT token (get_current_user dependency)
3. Routes layer retrieves organization (get_current_organization dependency)
4. Routes layer validates request schema using Pydantic
5. Routes layer calls service function
6. Services layer creates item in database
7. Services layer adds assignees to item
8. Services layer adds tags to item
9. Services layer logs activity for audit trail
10. Services layer returns created item
11. Routes layer returns 201 Created response with item object

---

### 3. Item Update with Change Tracking

*Linked Files:*
- app/routes.py (update_existing_item endpoint)
- app/services.py (update_item function)
- app/models.py (Item, ActivityLog models)

*Steps:*
1. Client sends PUT request to /items/{id} with updates
2. Server performs authentication and organization checks
3. Server retrieves existing item from database
4. Server tracks changes (comparing old vs new values)
5. Server updates item fields in database
6. Server updates assignees if specified
7. Server updates tags if specified
8. Server logs activity with detailed change history (field: {from, to})
9. Server returns updated item with 200 OK

---

### 4. Multi-Tenancy Data Isolation

*Linked Files:*
- app/dependencies.py (get_current_organization)
- app/models.py (Organization, User models)
- app/services.py (all service functions)

*Process:*
1. User authenticates with JWT token
2. Token is decoded to extract user ID
3. User record is retrieved, including organization_id
4. get_current_organization() dependency retrieves Organization object
5. All subsequent database queries are automatically filtered by organization_id
6. Data isolation ensures:
   - Items WHERE organization_id = user's org
   - Users WHERE organization_id = user's org
   - Teams WHERE organization_id = user's org
   - Webhooks WHERE organization_id = user's org
7. Users from different organizations can never access each other's data

---

### 5. Analytics Data Aggregation

*Linked Files:*
- app/routes.py (analytics endpoints)
- app/services.py (get_item_analytics, get_usage_analytics)
- app/models.py (Item, UsageLog models)

*Steps:*
1. Client sends GET request to /analytics/items
2. Server authenticates user and retrieves organization_id
3. Server executes multiple aggregation queries:
   - Total items: SELECT COUNT(*) WHERE org_id=X
   - By status: SELECT status, COUNT(*) GROUP BY status WHERE org_id=X
   - By priority: SELECT priority, COUNT(*) GROUP BY priority WHERE org_id=X
   - Overdue items: WHERE due_date < NOW() AND status != DONE
   - Completed this week: WHERE completed_at >= (NOW() - 7 days)
   - Avg completion time: SELECT AVG(actual_hours)
4. Server aggregates all results into response object
5. Server returns analytics data:
   - total_items
   - by_status breakdown
   - by_priority breakdown
   - overdue_items count
   - completed_this_week count
   - avg_completion_time_hours

---

### 6. Item Listing with Search Functionality

*Linked Files:*
- app/routes.py (list_items endpoint)
- app/services.py (get_items function)

*Steps:*
1. Client sends GET request to /items with optional filters including search text
2. Routes layer verifies JWT token (get_current_user dependency)
3. Routes layer retrieves organization (get_current_organization dependency)
4. Routes layer validates request schema using Pydantic
5. Routes layer calls service function with search text
6. Services layer filters items based on title or description using the provided search text
7. Services layer returns filtered item list
8. Routes layer returns 200 OK response with item list

*Note:*
- The item listing now supports filtering by search text, allowing clients to find items by title or description.
<!-- END: Data Flow -->

---

<!-- START: External Dependencies -->
## 2.4 External Dependencies

*Linked Files:*
- requirements.txt
- pyproject.toml
- docker-compose.yml
- .env.example

### Runtime Dependencies

The application relies on the following external libraries and services:

#### 1. *Core Framework*
- *FastAPI* (0.104+)
  - Purpose: Web framework for building APIs
  - Features: Async support, automatic validation, OpenAPI docs
  - Installation: pip install fastapi

- *Uvicorn*
  - Purpose: ASGI server for running FastAPI
  - Features: High performance, async support
  - Installation: pip install uvicorn[standard]

#### 2. *Database*
- *SQLAlchemy* (2.0+)
  - Purpose: ORM for database operations
  - Features: Relationship management, query building, migrations
  - Installation: pip install sqlalchemy

- *SQLite* (Development) / *PostgreSQL* (Production)
  - Purpose: Data persistence
  - SQLite: Built-in, file-based database
  - PostgreSQL: Production-grade relational database
  - PostgreSQL Installation: pip install psycopg2-binary

#### 3. *Authentication & Security*
- *python-jose[cryptography]*
  - Purpose: JWT token creation and validation
  - Features: HS256 algorithm, token expiration
  - Installation: pip install python-jose[cryptography]

- *passlib[bcrypt]*
  - Purpose: Password hashing
  - Features: Bcrypt algorithm, secure password storage
  - Installation: pip install passlib[bcrypt]

- *python-multipart*
  - Purpose: Form data and file upload handling
  - Installation: pip install python-multipart

#### 4. *Validation*
- *Pydantic* (2.5+)
  - Purpose: Data validation and serialization
  - Features: Type hints, automatic validation, JSON schema
  - Installation: pip install pydantic

#### 5. *Deployment*
- *Docker*
  - Purpose: Containerization
  - Configuration: Dockerfile, docker-compose.yml
  - Services: app, database (PostgreSQL), nginx

- *Nginx* (Optional)
  - Purpose: Reverse proxy, load balancing, SSL termination
  - Configuration: nginx.conf

### External Services (Optional/Future)

#### 1. *Email Service*
- *Purpose*: User notifications, password resets
- *Options*: SendGrid, AWS SES, Mailgun
- *Integration*: SMTP or REST API

#### 2. *File Storage*
- *Purpose*: Attachment storage
- *Options*: AWS S3, Google Cloud Storage, Azure Blob Storage
- *Current*: Local filesystem (./uploads)

#### 3. *Monitoring & Logging*
- *Purpose*: Application monitoring, error tracking
- *Options*: 
  - Sentry (error tracking)
  - Datadog (APM)
  - ELK Stack (logging)
  - Prometheus + Grafana (metrics)

#### 4. *Caching*
- *Purpose*: Performance optimization
- *Options*: Redis, Memcached
- *Use Cases*: Session storage, rate limiting, query caching

#### 5. *Message Queue*
- *Purpose*: Async task processing (webhooks, notifications)
- *Options*: Celery + Redis, RabbitMQ, AWS SQS
- *Use Cases*: Webhook delivery, email sending, background jobs

#### 6. *Payment Processing*
- *Purpose*: Subscription billing
- *Options*: Stripe, PayPal, Paddle
- *Integration*: Webhook-based subscription management

### Development Dependencies

- *pytest* - Testing framework
- *black* - Code formatting
- *flake8* - Linting
- *mypy* - Type checking
- *alembic* - Database migrations

### Environment Variables

The application uses the following environment variables:

bash
# Database
DATABASE_URL=postgresql://user:password@host/database

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Application
DEBUG=False
LOG_LEVEL=INFO

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Storage (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn


### Dependency Management

*Using Poetry* (Recommended):
bash
poetry install
poetry add <package>
poetry update


*Using pip*:
bash
pip install -r requirements.txt


*requirements.txt*:

fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.5.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
psycopg2-binary>=2.9.9  # For PostgreSQL


<!-- END: External Dependencies -->

---

## Summary

The Enterprise Todo Platform is built with a *clean, layered architecture* that emphasizes:

1. *Scalability*: Multi-tenant design, stateless API, database connection pooling
2. *Security*: JWT authentication, RBAC, password hashing, API key management
3. *Maintainability*: Clear separation of concerns, dependency injection, comprehensive logging
4. *Extensibility*: Webhook support, plugin-ready architecture, API-first design
5. *Observability*: Activity logs, usage analytics, request timing, error tracking

The architecture supports the platform's goal of reaching *$10M ARR* through:
- *Multi-tenancy* enabling thousands of organizations
- *Subscription tiers* with feature gating
- *API-first design* enabling integrations and ecosystem growth
- *Enterprise features* (RBAC, webhooks, analytics, audit logs)
- *Production-ready* infrastructure with Docker, monitoring, and scalability

---

*Last Updated*: 2025-12-06  
*Version*: 2.0.0  
*Source Repository*: test_small_repo_python