from configparser import ConfigParser
import os
from pathlib import Path
from loguru import logger


class Configuration:
    """Singleton Configuration class that reads settings from a config file.

    Attributes:
        DEBUG (bool): Debug mode flag.
        ROOT_PATH (str): Root path for the application.
        DATABASE_URL (str): URL for the database connection.
        SECRET_KEY (str): Secret key for JWT token.
        EXPIRATION_TIME (int): Expiration time for JWT token.
        REFRESH_EXPIRATION_TIME (int): Expiration time for JWT refresh token.

    This class uses the singleton pattern to ensure only one instance
    of the configuration is ever created.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file: str = "config.ini"):
        """Initializes the Configuration class by setting up the configuration
        parser and reading the config file. This method is only called if the
        instance does not exist yet.

        Args:
            config_file (str, optional): Config file name. Defaults to
                                                            "config.ini".
        """
        if not hasattr(self, "initialized"):
            config = ConfigParser()
            config_path = (
                Path(__file__).resolve().parent.parent.parent / config_file
            )

            try:
                config.read(config_path)

                # Server
                self.HOST = config.get("SERVER", "HOST")
                self.PORT = int(config.getint("SERVER", "PORT"))
                self.ROOT_PATH = config.get("SERVER", "ROOT_PATH")
                self.RELOAD = config.getboolean("SERVER", "RELOAD")

                # Application
                self.DEBUG = config.getboolean("APP", "DEBUG")

                # Logging
                self.LOG_LEVEL = config.get("LOGGING", "LEVEL")
                self.LOG_FILE = config.get("LOGGING", "FILE")

                # Database
                self.DATABASE_URL = config.get("DATABASE", "DATABASE_URL")

                # Jwt Token
                self.ALGORITHM = config.get("TOKEN", "ALGORITHM")
                self.SECRET_KEY = config.get("TOKEN", "SECRET_KEY")
                self.EXPIRATION_TIME = config.getint(
                    "TOKEN", "EXPIRATION_TIME"
                )
                self.REFRESH_EXPIRATION_TIME = config.getint(
                    "TOKEN", "REFRESH_EXPIRATION_TIME"
                )

                self.initialized = True

            except Exception as err:
                logger.error(
                    f"Reading `{config_file}` failed with error: {err}"
                )

    def set_env_variables(self):
        """Sets the configuration attributes as environment variables."""
        attributes = [
            "HOST",
            "PORT",
            "DEBUG",
            "ROOT_PATH",
            "DATABASE_URL",
            "ALGORITHM",
            "SECRET_KEY",
            "EXPIRATION_TIME",
            "REFRESH_EXPIRATION_TIME",
        ]

        for attr in attributes:
            os.environ[attr] = str(getattr(self, attr))


config = Configuration(
    "resources/development.ini"
)  # Configuration class instance
