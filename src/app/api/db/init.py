from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


from .base import Base
from ...settings.config import config


class DatabaseService:
    """
    A service class for managing database connections and sessions.

    Attributes:
        engine (Engine): The SQLAlchemy engine instance.
        SessionLocal (sessionmaker): A configured sessionmaker instance.

    Methods:
        __init__(database_url):
            Initializes the DatabaseService with the given database URL.

        get_session():
            Creates and returns a new database session.

        init_db():
            Initializes the database schema by creating all tables.
    """

    def __init__(self, database_url):
        try:
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
        except SQLAlchemyError as e:
            # TODO: log this error or handle it more appropriately
            raise HTTPException(
                status_code=500, detail=f"Failed to initialize database connection. {e}"
            )

    def get_session(self):
        try:
            return self.SessionLocal()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create session. {e}"
            )

    def init_db(self):
        try:
            Base.metadata.create_all(bind=self.engine)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to initialize database schema. {e}"
            )


try:
    db_service = DatabaseService(config.DATABASE_URL)
except HTTPException as e:
    raise e
