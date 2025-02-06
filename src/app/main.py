from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import SQLAlchemyError

from .api.db.init import DatabaseService, db_service
from .api.routes import auth, customer, health, order
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
        # database
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(customer.router, prefix="/customers", tags=["customers"])
app.include_router(order.router, prefix="/orders", tags=["orders"])


# Configure OIDC for OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Savannah Orders API",
        version="1.0.0",
        description="Savannah Orders API with OIDC Keycloak authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2AuthorizationCodeBearer": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": (
                        f"{config.KEYCLOAK_URL}/realms/{config.REALM_NAME}"
                        "/protocol/openid-connect/auth"
                    ),
                    "tokenUrl": (
                        f"{config.KEYCLOAK_URL}/realms/{config.REALM_NAME}"
                        "/protocol/openid-connect/token"
                    ),
                    "scopes": {"admin": "Admin role access"},
                }
            },
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


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
