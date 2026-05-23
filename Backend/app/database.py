"""
Closira — Database Configuration

Sets up SQLAlchemy with SQLite. This module provides:
1. Engine — the connection to the database
2. SessionLocal — a factory for database sessions
3. Base — the declarative base that all models inherit from
4. get_db() — a FastAPI dependency that provides a session per request

Why SQLAlchemy instead of raw SQL?
- Clean model definitions with Python classes
- Automatic table creation from models
- Database-agnostic — swap SQLite for PostgreSQL by changing the URL
- Built-in connection pooling and session management

Why check_same_thread=False for SQLite?
- SQLite restricts connections to the thread that created them by default
- FastAPI handles requests across multiple threads
- This flag relaxes that restriction, which is safe for our single-writer use case
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# The engine is the starting point for any SQLAlchemy application.
# It manages the connection pool and dialect (SQLite in our case).
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
    echo=settings.DEBUG,  # Log SQL statements when DEBUG=true (helpful during development)
)


# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
# SessionLocal creates new database sessions.
# autocommit=False  → we control when commits happen (explicit > implicit)
# autoflush=False   → we control when data is flushed to the DB
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------
# All ORM models will inherit from this Base class.
# It provides the metadata that SQLAlchemy uses to create tables.
# ---------------------------------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------------------------------
# FastAPI Dependency
# ---------------------------------------------------------------------------
# get_db() is a generator that provides a database session to each request.
# The session is automatically closed after the request completes (even on error).
#
# Usage in routers:
#   def my_endpoint(db: Session = Depends(get_db)):
#       ...
# ---------------------------------------------------------------------------
def get_db():
    """
    Provide a database session for a single request lifecycle.

    Yields a SQLAlchemy session and ensures it is closed after use,
    even if an exception occurs during the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
