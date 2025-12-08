## Authentication & Authorization

This codebase implements combined JWT-based user authentication, API key access for machine clients, and role-based authorization enforced via FastAPI dependencies.

Key components

- app/auth.py
  - Password hashing: get_password_hash() and verify_password() using passlib CryptContext (bcrypt).
  - JWT tokens: create_access_token(data, expires_delta) encodes payload (adds exp) with SECRET_KEY and HS256; decode_access_token(token) verifies and returns the payload.
  - API key generation: generate_api_key() returns a secure key prefixed with "sk_".
  - Constants: SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES control token behavior.

- app/models.py
  - User model: fields include id, email, username, hashed_password, role (UserRole enum), is_active, organization_id, last_login.
  - UserRole enum: OWNER, ADMIN, MEMBER, VIEWER used for RBAC checks.
  - APIKey model: key, name, organization_id, is_active, last_used_at, expires_at; Organization model links users and API keys.

- app/dependencies.py
  - HTTPBearer security is used to extract Authorization bearer tokens.
  - get_current_user: decodes JWT (decode_access_token), expects payload["sub"] = user.id, loads user from DB, ensures is_active, updates last_login and commits.
  - get_current_active_user: simple wrapper enforcing user.is_active.
  - get_current_organization: resolves organization for current_user and ensures org is active.
  - require_role(required_role): dependency factory implementing a role hierarchy mapping (VIEWER < MEMBER < ADMIN < OWNER); raises 403 if current_user.role is insufficient.
  - verify_api_key: reads X-API-KEY header, looks up APIKey row, ensures is_active and not expired, updates last_used_at, returns associated Organization.

- app/routes.py
  - Authentication endpoints: POST /auth/register (UserCreate -> create_user), POST /auth/login (UserLogin -> verifies password -> returns Token with access_token created via create_access_token), GET /auth/me (returns current user via get_current_active_user).
  - Authorization usage: routes use Dependencies to restrict actions (e.g., require_role(UserRole.ADMIN) for team creation, API key management, webhook management, and admin analytics endpoints). Several resource routes also depend on get_current_organization to enforce tenancy.

- app/services.py
  - create_user hashes passwords (get_password_hash) and persists User rows; create_api_key uses generate_api_key and persists APIKey rows; log_activity records actions for auditing.

Authentication flow summary

1. User registers via /auth/register -> create_user hashes password and creates User.
2. User logs in via /auth/login -> verify_password; on success create_access_token(data={"sub": user.id}) returns JWT bearer token.
3. Protected endpoints require Authorization: Bearer <token> (resolved via HTTPBearer -> get_current_user -> get_current_organization); role checks enforce RBAC via require_role.
4. Machine clients may use X-API-KEY header validated by verify_api_key, which returns the Organization context.

Source files


## Source Files
- app/auth.py
- app/dependencies.py
- app/models.py
- app/routes.py
- app/services.py
- app/schemas.py