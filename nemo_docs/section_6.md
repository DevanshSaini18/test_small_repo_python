# Database Engine, Sessions & Lifecycle

app/database.py provides the SQLAlchemy engine, SessionLocal factory, and Base declarative class used across the application.

Contents & usage:
- Engine: create_engine configured for SQLite by default (sqlite:///./test.db) with connect_args={"check_same_thread": False} to allow multi-threaded access in dev server. Production should replace this URL with a managed RDBMS (Postgres) and use connection pooling settings.
- SessionLocal: sessionmaker(autocommit=False, autoflush=False, bind=engine) returning scoped Session instances used by get_db dependency.
- Base: declarative_base used by app/models.py for ORM class definitions.
- get_db dependency: yields a session per request and ensures closure in a finally block — used widely in route dependencies and services.

Operational notes & gaps:
- No migrations: The project calls Base.metadata.create_all(bind=engine) in main.py to create tables at startup — fine for early development but migrations (Alembic) are required for production schema evolution.
- Indexes: models define index=True on common lookups but larger scale requires explicit index planning and query profiling.
- Backups & restore: not implemented inside code; docs/deployment.md references backup strategies. For production, point DB to external service and backup snapshots.


## Source Files
- app/database.py
- app/models.py
- main.py
- docs/deployment.md