import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from .api.routes import customers, health
from .settings.logging import logger
from .api.db.init import DatabaseService, db_service
from .settings.config import config
from .settings.logging import setup_logging


# DB Initializer
@asynccontextmanager
async def lifespan(app: FastAPI, service: DatabaseService = db_service):
    try:
        logger.info("Application is starting up...")
        setup_logging()
        service.init_db()
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
app.include_router(customers.router, prefix="/customers", tags=["customers"])


def main():
    uvicorn.run(
        "src.app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
    )


if __name__ == "__main__":
    main()
