from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# For SQLite need to set check_same_thread=False for multithreaded access
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Yield a new database session for each request.
    FastAPI's Depends will handle closing the session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
