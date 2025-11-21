import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable (Railway sets this automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway uses postgres://, but SQLAlchemy 1.4+ needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    if SessionLocal is None:
        raise Exception("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
