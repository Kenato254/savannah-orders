from fastapi import BackgroundTasks
from pydantic_core import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.schemas.customer import Customer

from ...settings.logging import logger
from ..models.order import Order as DBOrder
from ..schemas.order import Order, OrderCreate, OrderStatus
from ..services.sms_service import send_sms_task
from ..utils.common import update_time
from ..utils.customer import _get_customer_by_id
from ..utils.error_handler import handle_error_helper
from ..utils.order import _get_order_by_id


async def insert_order(
    db: AsyncSession,
    order_create: OrderCreate,
    background_tasks: BackgroundTasks,
    sms_service,
) -> Order:
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
        db_customer = await _get_customer_by_id(db, order_create.customer_id)
        customer = Customer.model_validate(db_customer)

        db_order = DBOrder(
            customer_id=customer.id,
            item=order_create.item,
            quantity=order_create.quantity,
            amount=(
                order_create.amount * order_create.quantity  # type: ignore
            ),
        )
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)

        await send_sms_task(
            background_tasks, sms_service, order_create, customer
        )

        logger.info("Order created successfully")
        return Order.model_validate(db_order)

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(400, f"Error creating order {e}")
        raise

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

        logger.info("Order retrieved successfully")
        return Order.model_validate(order)
    except ValidationError as e:
        await db.rollback()
        handle_error_helper(
            400, f"Error reading order with id: {order_id}. Error {e}"
        )
        raise

    except SQLAlchemyError as e:
        handle_error_helper(
            500, f"Error reading order with id: {order_id}. Error {e}"
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

        logger.info("Orders retrieved successfully")
        return [Order.model_validate(order) for order in orders]

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(400, f"Error reading orders. Error {e}")
        raise

    except SQLAlchemyError as e:
        handle_error_helper(500, f"Error reading orders. Error {e}")
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

        logger.info("Customer orders retrieved successfully")
        return [Order.model_validate(order) for order in orders]

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(
            400,
            f"Error retrieving orders for customer {customer_id}. Error {e}",
        )
        raise

    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            f"Error retrieving orders for customer {customer_id}. Error {e}",
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

        logger.info("Order updated successfully")
        return Order.model_validate(db_order)
    except ValidationError as e:
        await db.rollback()
        handle_error_helper(
            400, f"Error updating order with id {order_id}. Error {e}"
        )
        raise

    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(
            500, ("Error updating order with id:" f" {order_id}. Error {e}")
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

        logger.info("Order deleted successfully")
    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(
            500, f"Error deleting order with id: {order_id}. Error {e}"
        )
        raise
