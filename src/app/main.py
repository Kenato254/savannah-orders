import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from .settings.logging import logger
from .api.db.init import DatabaseService, db_service
from .settings.config import config
from .settings.logging import setup_logging


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


app = FastAPI(
    debug=config.DEBUG, root_path=config.ROOT_PATH, lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def test():
    return {"status": "running"}


def main():
    uvicorn.run(
        "src.app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
    )


if __name__ == "__main__":
    main()
