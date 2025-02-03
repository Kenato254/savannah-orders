from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.order import Order
from ..utils.error_handler import handle_error_helper


async def _get_order_by_id(db: AsyncSession, order_id: int) -> Order:
    """
    Retrieve an order by its ID from the database.

    Args:
        order_id (int): The ID of the order to retrieve.
        db (Session): The database session to use for the query.

    Returns:
        Order: The order object if found.

    Raises:
        HTTPException: If the order with the specified ID not found.
    """
    db_order_query = await db.execute(
        select(Order).filter(Order.id == order_id)
    )
    db_order = db_order_query.scalars().first()

    if db_order is None:
        handle_error_helper(404, f"Order with id: {order_id} not found!")
        raise
    return db_order
