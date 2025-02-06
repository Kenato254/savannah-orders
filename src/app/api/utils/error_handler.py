from fastapi import HTTPException
from pydantic_core import ValidationError

from ...settings.logging import logger


def handle_error_helper(error_code: int, message: str) -> None:
    """
    Logs an error message and raises an HTTPException based on
        the provided error code.

    Args:
        error_code (int): The HTTP status code representing the error.
        message (str): The error message to be logged and included in the
                                                                exception.

    Raises:
        HTTPException: An exception with the corresponding
                    HTTP status code and error message.
    """
    logger.error(f"Error {error_code}: {message}")
    raise HTTPException(status_code=error_code, detail=message)


def format_validation_error_msg(e: ValidationError) -> str:
    msg = ""
    for error in e.errors():
        msg = f"{error["msg"]}: {error["type"]} `{error["loc"][0]}`"
    return msg
