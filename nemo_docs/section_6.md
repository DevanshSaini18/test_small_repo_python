# Authentication & Authorization

Security primitives are implemented across app/auth.py and app/dependencies.py to support password-based login, JWT access tokens, API keys, and role-based authorization.

Auth primitives (app/auth.py):
- Password hashing & verification: passlib CryptContext with bcrypt scheme (get_password_hash, verify_password).
- JWT tokens: create_access_token and decode_access_token using python-jose with HS256. SECRET_KEY is generated in code for dev (secrets.token_urlsafe) — production must source this from a secure environment variable.
- API key generation: generate_api_key produces sk_-prefixed secrets using secrets.token_urlsafe.

Dependency layer (app/dependencies.py):
- HTTPBearer-based token reading: get_current_user decodes JWT, fetches user by id (payload["sub"]), ensures active user, updates last_login timestamp.
- get_current_active_user / get_current_organization: thin wrappers that enforce active user and active tenant checks.
- require_role(required_role): factory that enforces role hierarchy (viewer < member < admin < owner) for Admin/Owner-only endpoints.
- verify_api_key: header-based X-API-KEY check that looks up active APIKey, checks expiration, updates last_used_at and returns organization context.

Security notes:
- Token expiry is set to 24 hours in code (ACCESS_TOKEN_EXPIRE_MINUTES constant) but is configurable if replaced by env-based settings.
- Secrets in the code are placeholders; immediate change is required before production (use .env and secrets manager).
- RBAC is enforced at route-level through dependencies rather than inline checks; this yields composable, testable authorization logic.


## Source Files
- app/auth.py
- app/dependencies.py
- app/models.py