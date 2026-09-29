from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from app.core.config import settings
from urllib.parse import quote_plus


DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_NAME}"
)
engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base=declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import app.models