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
        """Initializes the Configuration class by loading the .env file
        and setting up configuration attributes from environment variables.
        """
        if not hasattr(self, "initialized"):
            load_dotenv()

            # Server
            self.HOST = os.getenv("HOST", "localhost")
            self.PORT = int(os.getenv("PORT", "8080"))
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

            # JWT Token
            self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
            self.SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
            self.EXPIRATION_TIME = int(os.getenv("EXPIRATION_TIME", "60"))
            self.REFRESH_EXPIRATION_TIME = int(
                os.getenv("REFRESH_EXPIRATION_TIME", "10080")
            )

            # SMS
            self.AFRICASTALKING_CODE = os.getenv("AFRICASTALKING_CODE", "")
            self.AFRICASTALKING_USERNAME = os.getenv(
                "AFRICASTALKING_USERNAME", ""
            )
            self.AFRICASTALKING_API_KEY = os.getenv(
                "AFRICASTALKING_API_KEY", ""
            )

            self.initialized = True


config = Configuration()
