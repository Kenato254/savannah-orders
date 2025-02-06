from fastapi import BackgroundTasks, HTTPException, status
from pydantic_core import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.schemas.customer import Customer

from ...settings.logging import logger
from ..models.order import Order as DBOrder
from ..schemas.order import Order, OrderCreate, OrderStatus
from ..services.sms_service import send_sms_task
from ..utils.common import update_time
from ..utils.customer import _get_customer_by_id
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
        db (AsyncSession): The database session to use for the operation.
        order_create (OrderCreate): The order data to insert.
        background_tasks (BackgroundTasks): Background tasks for sending SMS.
        sms_service: The SMS service to use for notifications.

    Returns:
        Order: The created order object.

    Raises:
        HTTPException: If there is an error during the database operation.
    """
    try:
        db_customer = await _get_customer_by_id(db, order_create.customer_id)
        customer = Customer.model_validate(db_customer)

        db_order = DBOrder(
            customer_id=customer.id,
            item=order_create.item,
            quantity=order_create.quantity,
            amount=order_create.amount * order_create.quantity,  # type: ignore
        )
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)

        await send_sms_task(
            background_tasks, sms_service, order_create, customer
        )

        logger.info(f"Order with ID {db_order.id} created successfully")
        return Order.model_validate(db_order)

    except NoResultFound:
        await db.rollback()
        logger.error(f"Customer with ID {order_create.customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {order_create.customer_id} not found",
        )

    except ValidationError as e:
        await db.rollback()
        logger.error(f"Validation error while creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the order",
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order:
    """
    Retrieve an order by its ID from the database.

    Args:
        db (AsyncSession): The database session to use for the query.
        order_id (int): The ID of the order to retrieve.

    Returns:
        Order: The order object if found.

    Raises:
        HTTPException: If the order with the given ID does not exist.
        HTTPException: If there is an error reading the order from
                                                            the database.
    """
    try:
        order = await _get_order_by_id(db, order_id)

        logger.info(f"Order with ID {order_id} retrieved successfully")
        return Order.model_validate(order)

    except NoResultFound:
        logger.error(f"Order with ID {order_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    except ValidationError as e:
        logger.error(f"Validation error for order with ID {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}",
        )

    except SQLAlchemyError as e:
        logger.error(
            f"Database error while retrieving order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the order",
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def get_all_orders(
    db: AsyncSession, skip: int = 0, limit: int = 10
) -> list[Order]:
    """
    Retrieve a list of orders from the database with pagination.

    Args:
        db (AsyncSession): The database session to use for the query.
        skip (int): The number of records to skip before starting to
                                                collect the result set.
        limit (int): The maximum number of records to return. Defaults to 10.

    Returns:
        list[Order]: A list of Order objects.

    Raises:
        HTTPException: If there is an error querying the database.
    """
    try:
        orders_query = await db.execute(
            select(DBOrder).offset(skip).limit(limit)
        )
        orders = orders_query.scalars().all()

        logger.info(f"Retrieved {len(orders)} orders successfully")
        return [Order.model_validate(order) for order in orders]

    except ValidationError as e:
        logger.error(f"Validation error while retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}",
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving orders",
        )

    except Exception as e:
        logger.error(f"Unexpected error while retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def get_orders_by_customer_id(
    db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 10
) -> list[Order]:
    """
    Retrieve orders for a specific customer with pagination.

    Args:
        db (AsyncSession): The database session to use for the query.
        customer_id (int): The ID of the customer whose orders should
                                                                be fetched.
        skip (int): The number of records to skip before starting
                                                to collect the result set.
        limit (int): The maximum number of records to return. Defaults to 10.

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

        logger.info(
            (
                f"Retrieved {len(orders)} orders "
                f"for customer with ID {customer_id}"
            )
        )
        return [Order.model_validate(order) for order in orders]

    except NoResultFound:
        logger.error(f"Customer with ID {customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )

    except ValidationError as e:
        logger.error(
            "Validation error while retrieving orders"
            f" for customer with ID {customer_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}",
        )

    except SQLAlchemyError as e:
        logger.error(
            (
                "Database error while retrieving orders "
                f"for customer with ID {customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving orders",
        )

    except Exception as e:
        logger.error(
            (
                "Unexpected error while retrieving orders "
                f"for customer with ID {customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def update_order_by_id(
    db: AsyncSession, order_id: int, order_update: OrderStatus
) -> Order:
    """
    Update an order's information in the database.

    Args:
        db (AsyncSession): The database session to use for the update.
        order_id (int): The ID of the order to update.
        order_update (OrderStatus): The updated order information.

    Returns:
        Order: The updated order object.

    Raises:
        HTTPException: If the order is not found or there is an error
                                                        during the update.
    """
    try:
        db_order = await _get_order_by_id(db, order_id)
        db_order.status = order_update
        await update_time(db_order)
        await db.commit()
        await db.refresh(db_order)

        logger.info(f"Order with ID {order_id} updated successfully")
        return Order.model_validate(db_order)

    except NoResultFound:
        await db.rollback()
        logger.error(f"Order with ID {order_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    except ValidationError as e:
        await db.rollback()
        logger.error(
            f"Validation error while updating order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Database error while updating order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the order",
        )

    except Exception as e:
        await db.rollback()
        logger.error(
            f"Unexpected error while updating order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def delete_order_by_id(db: AsyncSession, order_id: int) -> None:
    """
    Deletes an order from the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        order_id (int): The ID of the order to delete.

    Raises:
        HTTPException: If the order is not found or there is an error
                                                        during deletion.
    """
    try:
        db_order = await _get_order_by_id(db, order_id)
        await db.delete(db_order)
        await db.commit()

        logger.info(f"Order with ID {order_id} deleted successfully")

    except NoResultFound:
        await db.rollback()
        logger.error(f"Order with ID {order_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Database error while deleting order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the order",
        )

    except Exception as e:
        await db.rollback()
        logger.error(
            f"Unexpected error while deleting order with ID {order_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
