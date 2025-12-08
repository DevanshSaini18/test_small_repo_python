## Database Setup & Migrations

Overview

This project uses SQLAlchemy core + ORM for its persistence layer. The database configuration, session factory, and declarative base are defined in app/database.py; all ORM models are declared in app/models.py and register themselves on the shared Base. At application startup main.py invokes SQLAlchemy's metadata.create_all to ensure schema objects exist.

Engine and Connection URL

- The engine is created in app/database.py via create_engine(SQLALCHEMY_DATABASE_URL).
- The repository default URL is sqlite:///./test.db. For SQLite the engine is created with connect_args={"check_same_thread": False} to allow multi-threaded access from the ASGI server.

Session management

- A scoped session factory is provided as SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine).
- A dependency generator get_db() yields a new SessionLocal instance per request and ensures db.close() in a finally block. This dependency is consumed by route/service functions via FastAPI's Depends.

Declarative Base & Models

- Base = declarative_base() is the shared metadata registry used by all models in app/models.py (association tables, enums, and ORM classes like Organization, User, Item, Team, Tag, Comment, Attachment, APIKey, Webhook, UsageLog, ActivityLog, etc.).
- Models import Base from app.database so their Table/Column definitions populate Base.metadata.

Schema Creation at Startup

- main.py calls Base.metadata.create_all(bind=engine) during application initialization, causing SQLAlchemy to create tables for all registered models against the configured engine at runtime.

Migrations (current project state)

- The codebase relies on SQLAlchemy's metadata.create_all for creating schema objects on startup (see main.py). There are no migration scripts or a migration tool (e.g., Alembic) present in the repository under the application sources.

Files

- app/database.py — engine, SessionLocal, Base, get_db dependency.
- app/models.py — ORM models and association tables that populate Base.metadata.
- main.py — application bootstrap that invokes Base.metadata.create_all(bind=engine) at startup.

This setup centralizes the engine/session/base definitions and wires model metadata into application startup creation of schema objects via create_all.

## Source Files
- app/database.py
- app/models.py
- main.py