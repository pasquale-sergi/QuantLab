from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.database_url

if database_url.startswith("sqlite"):
    engine = create_engine(database_url, future=True, connect_args={"check_same_thread": False})
else:
    engine = create_engine(database_url, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
