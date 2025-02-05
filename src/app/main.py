from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from .api.db.init import DatabaseService, db_service
from .api.routes import customer, health, order
from .settings.config import config
from .settings.logging import logger, setup_logging
from .settings.sms.init import get_sms_service


# Initializer
@asynccontextmanager
async def lifespan(app: FastAPI, service: DatabaseService = db_service):
    try:
        logger.info("Application is starting up...")
        # logs
        setup_logging()
        # satabase
        await service.init_db()
        # sms
        get_sms_service()
        yield
    except SQLAlchemyError as e:
        logger.error(f"Database error during startup: {e}")
        raise
    finally:
        logger.info("Application is shutting down...")


# App Initializer
app = FastAPI(
    debug=config.DEBUG, root_path=config.ROOT_PATH, lifespan=lifespan
)

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(customer.router, prefix="/customers", tags=["customers"])
app.include_router(order.router, prefix="/orders", tags=["orders"])


# Main
def main():
    uvicorn.run(
        "src.app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
    )


if __name__ == "__main__":
    main()
