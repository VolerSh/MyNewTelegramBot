from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# We will use SQLite for simplicity. The database will be created in the project root.
DATABASE_URL = "sqlite:///./marketplace_deals.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    Base.metadata.create_all(bind=engine)