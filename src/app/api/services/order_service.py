from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.order import Order as DBOrder
from ..schemas.order import Order, OrderCreate, OrderStatus
from ..utils.common import update_time
from ..utils.customer import _get_customer_by_id
from ..utils.error_handler import handle_error_helper
from ..utils.order import _get_order_by_id


async def insert_order(db: AsyncSession, order: OrderCreate) -> Order:
    """
    Inserts a new order into the database.

    Args:
        db (Session): The database session to use for the operation.
        order (OrderCreate): The order data to insert.

    Returns:
        Order: The created order object.

    Raises:
        SQLAlchemyError: If there is an error during the database operation.
    """
    try:
        customer = await _get_customer_by_id(db, order.customer_id)
        db_order = DBOrder(
            customer_id=customer.id,
            item=order.item,
            amount=order.amount,  # type: ignore
        )
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)
        return Order.model_validate(db_order)
    except SQLAlchemyError as e:
        handle_error_helper(500, f"Error creating an order {e}")
        raise


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order:
    """
    Retrieve an order by its ID from the database.

    Args:
        db (Session): The database session to use for the query.
        order_id (int): The ID of the order to retrieve.

    Returns:
        DBOrder: The order object if found.

    Raises:
        HTTPException: If the order with the given ID does not exist.
        HTTPException: If there is an error reading the order from
                                                            the database.
    """
    try:
        order = await _get_order_by_id(db, order_id)
        return Order.model_validate(order)
    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            (
                "Error reading order with id:"
                f" {order_id}. Error {e.with_traceback}"
            ),
        )
        raise


async def get_all_orders(
    db: AsyncSession, skip: int = 0, limit: int = 10
) -> list[Order]:
    """
    Retrieve a list of orders from the database with pagination.

    Args:
        db (Session): The database session to use for the query.
        skip (int): The number of records to skip before starting to collect
                                                                the result set.
        limit (int, optional): The maximum number of records to return.
                                                                Defaults to 10.

    Returns:
        list[Order]: A list of Order objects.

    Raises:
        SQLAlchemyError: If there is an error querying the database.
    """
    try:
        orders_query = await db.execute(
            select(DBOrder).offset(skip).limit(limit)
        )
        orders = orders_query.scalars().all()

        return [Order.model_validate(order) for order in orders]
    except SQLAlchemyError as e:
        handle_error_helper(
            500, f"Error reading orders. Error {e.with_traceback}"
        )
        raise


async def get_orders_by_customer_id(
    db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 10
) -> list[Order]:
    """
    Retrieve orders for a specific customer with pagination.

    Args:
        db (Session): The database session to use for the query.
        customer_id (int): The ID of the customer whose orders should be
                                                                fetched.
        skip (int): The number of records to skip before starting
                                                to collect the result set.
        limit (int, optional): The maximum number of
                                        records to return. Defaults to 10.

    Returns:
        list[Order]: A list of Order objects for the specified customer.

    Raises:
        HTTPException: If there is an error querying the database.
    """
    try:
        orders_query = await db.execute(
            select(DBOrder)
            .filter(DBOrder.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
        )
        orders = orders_query.scalars().all()

        return [Order.model_validate(order) for order in orders]
    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            (
                "Error retrieving orders for customer"
                f" {customer_id}. Error {e.with_traceback}"
            ),
        )
        return []


async def update_order_by_id(
    db: AsyncSession, order_id: int, order_update: OrderStatus
) -> Order:
    """
    Update an order's information in the database.

    Args:
        db (Session): The database session to use for the update.
        order_id (int): The ID of the order to update.
        order_update (OrderUpdate): The updated order information.

    Returns:
        Order: The updated order object.

    Raises:
        SQLAlchemyError: If there is an error during the update process.
    """
    try:
        db_order = await _get_order_by_id(db, order_id)
        db_order.status = order_update
        await update_time(db_order)
        await db.commit()
        await db.refresh(db_order)
        return Order.model_validate(db_order)
    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(
            500,
            (
                "Error updating order with id:"
                f" {order_id}. Error {e.with_traceback}"
            ),
        )
        raise


async def delete_order_by_id(db: AsyncSession, order_id: int) -> None:
    """
    Deletes an order from the database.

    Args:
        db (Session): The database session to use for the operation.
        order_id (int): The ID of the order to delete.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there is an error during the deletion process,
            the transaction is rolled back and an error is logged.
    """
    try:
        db_order = await _get_order_by_id(db, order_id)
        await db.delete(db_order)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(
            500,
            (
                "Error deleting order with id:"
                f"{order_id}. Error {e.with_traceback}"
            ),
        )
        raise
