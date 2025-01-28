import logging
import sys
from pathlib import Path
from loguru import logger

from .config import config


def create_log_directory(log_path: str) -> Path:
    """Ensure the logs directory exists."""
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir / log_path


def configure_loguru(log_file: Path) -> None:
    """Configure Loguru logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        ),
        level="DEBUG",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(
        log_file,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        format="[{time:YYYY-MM-DD HH:mm:ss}] | {level} | {message}",
        level="INFO",
    )


class InterceptHandler(logging.Handler):
    """Redirect standard logging messages to Loguru."""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except KeyError:
            level = record.levelno
        logger.log(level, record.getMessage())


def redirect_standard_logs():
    """Redirect standard logging to Loguru."""
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
    for name in logging.root.manager.loggerDict.keys():
        if name.startswith("uvicorn"):
            logging.getLogger(name).handlers = [InterceptHandler()]


def setup_logging():
    """Set up the application's logging. Called during application startup"""
    log_file = create_log_directory(config.LOG_FILE)
    configure_loguru(log_file)
    redirect_standard_logs()


setup_logging()
