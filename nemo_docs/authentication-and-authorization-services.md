# Authentication and Authorization Services
Supports JWT-backed login/register, RBAC, and API-key verification for the multi-tenant todo platform.

## Credential and token utilities
- Passwords hashed via passlib bcrypt; tokens minted with jose, HS256, a 24‑hour expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`), and a `sub` claim; `decode_access_token` returns the payload or `None` so guards can react to invalid/expired tokens.
- API keys generated as `sk_{...}` secrets via `generate_api_key` for service-to-service access and stored with expiration metadata.

## FastAPI authentication endpoints
| Endpoint | Description | Guard & Schemas |
| --- | --- | --- |
| `POST /auth/register` | Validates unique email and organization, hashes the password in `create_user`, logs activity, and returns `UserRead`. | `UserCreate` ➜ `UserRead`, no auth but requires an existing organization. |
| `POST /auth/login` | Verifies credentials with `verify_password`, ensures the user is active, and issues the JWT `Token`. | `UserLogin` ➜ `Token`, open endpoint. |
| `GET /auth/me` | Returns the current authenticated user profile. | Guarded by `get_current_active_user`, responds with `UserRead`. |

## Authorization dependencies
- `get_current_user` uses `HTTPBearer`, decodes the JWT, looks up the `User`, enforces `is_active`, updates `last_login`, and keeps the organization in scope; this organization context ensures queries like the new `search_text` filter applied in `GET /items` remain tenant-scoped.
- `get_current_active_user` and `get_current_organization` ensure actions occur within an active tenant before business logic (including optional search_text filters) runs.
- `require_role` compares the `UserRole` hierarchy (`viewer < member < admin < owner`) to gate Admin/Owner APIs.
- `verify_api_key` reads `X-Api-Key`, confirms the key row is active/unexpired, updates `last_used_at`, and returns the owning `Organization` so API-key calls map to the right tenant.

## API key lifecycle
- `create_api_key` (service + `APIKeyCreate`/`APIKeyRead`) pairs generated secrets with organization, optional expiration, and audit timestamps; `get_api_keys` lists them for Admin users.
- The `APIKey` model stores `is_active`, `expires_at`, and `last_used_at`; the verification dependency enforces those flags before surfacing the organization to downstream routes.

## Source Files
- app/auth.py
- app/routes.py
- app/dependencies.py
- app/services.py
- app/schemas.py
- app/models.py