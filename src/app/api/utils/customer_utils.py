from ..schemas.customer import CustomerUpdate, Customer
from .error_handler import handle_error_helper


def update_customer_helper(
    db_user: Customer, customer_update: CustomerUpdate
) -> None:
    """
    Updates the fields of a Customer object with the values
    provided in a CustomerUpdate object.

    Args:
        db_user (Customer): The Customer object to be updated.
        customer_update (CustomerUpdate): An object containing
            the fields and values to update in the Customer object.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the update process,
            an error is logged with a 400 status code and the error message.
    """
    try:
        for field, value in customer_update:
            setattr(db_user, field, value)
    except Exception as e:
        handle_error_helper(
            400,
            (
                "Bad Request updating user with id:"
                f"{db_user.created_at}. Error {e.with_traceback}"
            ),
        )
