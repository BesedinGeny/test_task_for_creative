from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settigns import settings

# PostgresSQL Client
engine = create_engine(settings.POSTGRES_DATABASE_URI,
                       pool_pre_ping=True, pool_size=settings.POOL_SIZE, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
