from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db.session import get_db

router = APIRouter()


@router.get("/", summary="Health Check")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    This endpoint is used to check the health status of the
                application and its database connection.

    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "running", "database": "connected"}
    except Exception:
        return {"status": "running", "database": "unavailable"}
