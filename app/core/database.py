# app/core/database.py

from sqlmodel import SQLModel, create_engine, Session
from .config import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    # Import all models to ensure they're registered with SQLModel
    from app.models.student import Student
    from app.models.grade import Grade

    SQLModel.metadata.create_all(engine)


def get_session():
    def _get():
        with Session(engine) as session:
            yield session

    return _get