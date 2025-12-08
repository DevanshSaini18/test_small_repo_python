# Pydantic Schemas (API Contracts)

app/schemas.py contains the request and response models used throughout the API. These Pydantic models define validation, defaulting, and serialization for the HTTP surface.

Key characteristics:
- Pattern: Base -> Create/Update -> Read for most domain entities (Organization, User, Team, Tag, Item, Comment, APIKey, Webhook).
- orm_mode enabled on Read models so SQLAlchemy ORM instances can be returned directly from routes and serialized into JSON.
- Typed fields and default values: Enums from app.models are reused (ItemStatus, PriorityLevel, UserRole, SubscriptionTier) to maintain alignment between API and DB layers.
- Compound & nested shapes: ItemRead contains nested lists of assignees (List[UserRead]) and tags (List[TagRead]) to represent relationships.
- Analytics shapes: ItemAnalytics and UsageAnalytics provide aggregated response schemas for operational endpoints.

Why it matters:
These schemas are the explicit API contract; changes here impact backwards compatibility, clients, and documentation (auto-generated via FastAPI docs). They also centralize validations like email formats and datetime typing.


## Source Files
- app/schemas.py