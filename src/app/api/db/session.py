from fastapi import Depends

from .init import DatabaseService, db_service


def get_db(service: DatabaseService = Depends(lambda: db_service)):
    """
    Dependency that provides a database session to be used in FastAPI routes.

    Yields:
        SessionLocal: A SQLAlchemy database session.

    Ensures that the database session is properly closed after use.
    """
    try:
        db = service.get_session()
        yield db
    finally:
        db.close()
