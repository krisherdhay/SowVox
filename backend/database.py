import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

IS_RAILWAY = os.environ.get("RAILWAY_ENVIRONMENT")

if IS_RAILWAY:
    DATABASE_URL = "sqlite:////data/sowvox.db"
else:
    DATABASE_URL = "sqlite:///./test_sow.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
