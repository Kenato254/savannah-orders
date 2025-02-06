import os

from dotenv import load_dotenv


class Configuration:
    """Singleton Configuration class that reads settings from .env file or
    environment variables.

    Attributes:
        ...

    This class uses the singleton pattern to ensure only one instance
    of the configuration is ever created. It prioritizes environment variables
    over .env file values for settings.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.reload_config()
            self.initialized = True

    def reload_config(self):
        """Reloads the configuration from the .env file."""
        # Clear existing environment variables that might be set from .env
        for key in list(os.environ.keys()):
            if key in [
                'HOST',
                'PORT',
                'ROOT_PATH',
                'RELOAD',
                'DEBUG',
                'LOG_LEVEL',
                'LOG_FILE',
                'DATABASE_URL',
                'AFRICASTALKING_CODE',
                'AFRICASTALKING_USERNAME',
                'AFRICASTALKING_API_KEY',
                'REALM_NAME',
                'KEYCLOAK_URL',
                'KEYCLOAK_CLIENT_ID',
            ]:
                os.environ.pop(key, None)

        # Reload .env file
        load_dotenv()

        # Server
        self.HOST = os.getenv("HOST", "localhost")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.ROOT_PATH = os.getenv("ROOT_PATH", "/api/v1")
        self.RELOAD = os.getenv("RELOAD", "True").lower() == 'true'

        # Application
        self.DEBUG = os.getenv("DEBUG", "True").lower() == 'true'

        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "debug")
        self.LOG_FILE = os.getenv("LOG_FILE", "app.log")

        # Database
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", "sqlite+aiosqlite:///./test.db"
        )

        # SMS
        self.AFRICASTALKING_CODE = os.getenv("AFRICASTALKING_CODE", "")
        self.AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME", "")
        self.AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY", "")

        # Keycloak
        self.REALM_NAME = os.getenv("REALM_NAME", "")
        self.KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "")
        self.KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "")
        self.KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")


config = Configuration()
config.reload_config()
