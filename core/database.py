"""
Database Infrastructure Module for ChaloGhumo.

This module configures the primary relational database infrastructure using 
SQLAlchemy. It provides the engine, session factory, and a dependency-ready 
database session generator for FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

# --- Connection Configuration ---
# Construct the standard PostgreSQL connection URI from global settings.
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

# The engine serves as the central source of connections to the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal is the factory for individual database sessions.
# Configured for manual commit/flush for precise transaction control.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all declarative relational models.
Base = declarative_base()


def get_db():
    """
    FastAPI Dependency: Provides a transactional database session.
    
    Ensures that the session is automatically closed after the request is 
    fulfilled, preventing connection leaks.
    
    Yields:
        An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
