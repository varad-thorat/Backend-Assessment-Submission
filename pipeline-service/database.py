from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_db") # Get database URL from environment variable


engine = create_engine(DATABASE_URL) # Create SQLAlchemy engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Create SessionLocal class


Base = declarative_base() # Create Base class for models

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from models.customer import Customer
    Base.metadata.create_all(bind=engine)