from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.customer import Customer
from ..schemas.customer import CustomerUpdate
from .error_handler import handle_error_helper


async def update_customer_helper(
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
        for key, value in customer_update.model_dump(
            exclude_unset=True
        ).items():
            setattr(db_user, key, value)
    except Exception as e:
        handle_error_helper(
            400,
            (
                "Bad Request updating user with id:"
                f"{db_user.created_at}. Error {e.with_traceback}"
            ),
        )


async def _get_customer_by_id(db: AsyncSession, customer_id: int) -> Customer:
    """
    Retrieve an customer by its ID from the database.

    Args:
        customer_id (int): The ID of the customer to retrieve.
        db (Session): The database session to use for the query.

    Returns:
        Customer: The customer object if found.

    Raises:
        HTTPException: If the customer with the specified ID not found.
    """
    db_customer_query = await db.execute(
        select(Customer).filter(Customer.id == customer_id)
    )

    db_customer = db_customer_query.scalar_one_or_none()

    if db_customer is None:
        handle_error_helper(404, f"Customer with id: {customer_id} not found!")
        raise
    return db_customer
