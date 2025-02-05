import africastalking  # type: ignore

from ..config import config


def initialize_africastalking():
    """
    Initializes the AfricasTalking API with the provided username
                                        and API key from the config.

    Returns:
        africastalking.SMS: The SMS service from the AfricasTalking API.
    """
    africastalking.initialize(
        username=config.AFRICASTALKING_USERNAME,
        api_key=config.AFRICASTALKING_API_KEY,
    )
    return africastalking.SMS


def get_sms_service():
    """
    Initializes and returns the SMS service using Africa's Talking API.

    Returns:
        object: An instance of the initialized Africa's Talking SMS service.
    """
    return initialize_africastalking()
