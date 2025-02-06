from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...settings.logging import logger
from ..auth.oidc import has_role
from ..db.session import get_db

router = APIRouter()


@router.get(
    "/", summary="Health Check", dependencies=[Depends(has_role("admin"))]
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.

    This endpoint is used to check the health status of the
                application and its database connection.

    """
    msg = {"status": "running", "database": "connected"}
    try:
        await db.execute(text("SELECT 1"))

        logger.info(f"System: {msg}")
        return msg
    except Exception as e:
        msg = {"status": "running", "database": "unavailable"}
        logger.error(f"System: {msg}. Error {str(e)}")
        return msg
