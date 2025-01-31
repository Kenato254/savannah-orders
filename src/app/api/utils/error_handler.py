from fastapi import HTTPException

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
    logger.error(message)
    match error_code:
        case 400:
            raise HTTPException(status_code=400, detail=message)
        case 401:
            raise HTTPException(status_code=401, detail=message)
        case 403:
            raise HTTPException(status_code=403, detail=message)
        case 404:
            raise HTTPException(status_code=404, detail=message)
        case 500:
            raise HTTPException(status_code=500, detail=message)
        case _:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {message}",
            )
