from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ...settings.config import config
from ..utils.error_handler import handle_error_helper
from .base import Base


class DatabaseService:
    """
    A service class for managing asynchronous database connections and
                                                                    sessions.

    Attributes:
        engine (Engine): The SQLAlchemy async engine instance.
        SessionLocal (sessionmaker): A configured async sessionmaker instance.

    Methods:
        __init__(database_url):
            Initializes the DatabaseService with the given database URL.

        get_session():
            Creates and returns a new asynchronous database session.

        init_db():
            Initializes the database schema by creating all tables.
    """

    def __init__(self, database_url):
        try:
            self.engine = create_async_engine(database_url, echo=True)
            self.SessionLocal = sessionmaker(
                self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            )
        except SQLAlchemyError as e:
            handle_error_helper(
                500, f"Failed to initialize database connection. {e}"
            )
            raise

    async def get_session(self):
        try:
            return self.SessionLocal()
        except SQLAlchemyError as e:
            handle_error_helper(500, f"Failed to create session. {e}")
            raise

    async def init_db(self):
        try:
            async with self.engine.begin() as conn:
                # await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        except SQLAlchemyError as e:
            handle_error_helper(
                500, f"Failed to initialize database schema. {e}"
            )
            raise


try:
    db_service = DatabaseService(config.DATABASE_URL)
except HTTPException as e:
    raise e
