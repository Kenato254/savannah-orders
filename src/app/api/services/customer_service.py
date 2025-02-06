from fastapi import HTTPException, status
from pydantic_core import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ...settings.logging import logger
from ..models.customer import Customer as DBCustomer
from ..models.order import Order as DBOrder
from ..schemas.customer import (
    Customer,
    CustomerCreate,
    CustomerOrders,
    CustomerUpdate,
)
from ..schemas.order import Order
from ..utils.customer import _get_customer_by_id, update_customer_helper
from ..utils.error_handler import format_validation_error_msg


async def insert_customer(
    db: AsyncSession, customer: CustomerCreate, user_id: str
) -> Customer:
    """
    Inserts a new customer into the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        customer (CustomerCreate): The customer data to insert.
        user_id (str): The user ID associated with the customer.

    Returns:
        Customer: The created customer.

    Raises:
        HTTPException: If there is an error during the database operation.
    """
    try:
        db_customer = DBCustomer(
            name=customer.name,
            phone_number=customer.phone_number,
            code=customer.code,
            user_id=user_id,
        )
        db.add(db_customer)
        await db.flush()

        await db.commit()
        await db.refresh(db_customer)

        logger.info("Customer created successfully")
        return Customer.model_validate(db_customer)

    except ValidationError as e:
        await db.rollback()
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Customer with the same user_id already exists.",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Customer:
    """
    Retrieve a customer by their ID from the database.

    Args:
        db (AsyncSession): The database session to use for the query.
        customer_id (int): The ID of the customer to retrieve.

    Returns:
        Customer: The customer object if found.

    Raises:
        HTTPException: If the customer with the given ID does not exist.
        HTTPException: If there is an error reading the customer from
                                                            the database.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)
        logger.info(f"Customer with ID {customer_id} retrieved successfully")
        return Customer.model_validate(db_customer)

    except NoResultFound:
        logger.error(f"Customer with ID {customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )

    except MultipleResultsFound:
        logger.error(f"Multiple customers found with ID {customer_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multiple customers found with ID {customer_id}",
        )

    except ValidationError as e:
        logger.error(
            f"Validation error for customer with ID {customer_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Validation error for customer with ID "
                f"{customer_id}: {format_validation_error_msg(e)}"
            ),
        )

    except SQLAlchemyError as e:
        logger.error(
            (
                "Database error while retrieving customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading customer with ID {customer_id}",
        )

    except Exception as e:
        logger.error(
            (
                "Unexpected error while retrieving customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def get_all_customers(
    db: AsyncSession, skip: int, limit: int
) -> list[Customer]:
    """
    Retrieve a list of customers from the database with pagination.

    Args:
        db (AsyncSession): The database session to use for the query.
        skip (int): The number of records to skip before starting to
                                                    collect the result set.
        limit (int): The maximum number of records to return.

    Returns:
        list[Customer]: A list of Customer objects.

    Raises:
        HTTPException: If there is an error querying the database.
    """
    try:
        customers_query = await db.execute(
            select(DBCustomer).offset(skip).limit(limit)
        )
        customers = customers_query.scalars().all()

        logger.info(f"Retrieved {len(customers)} customers successfully")
        return [Customer.model_validate(customer) for customer in customers]

    except ValidationError as e:
        logger.error(f"Validation error while retrieving customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {format_validation_error_msg(e)}",
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving customers",
        )

    except Exception as e:
        logger.error(f"Unexpected error while retrieving customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def update_customer_by_id(
    db: AsyncSession, customer_id: int, customer_update: CustomerUpdate
) -> Customer:
    """
    Update a customer's information in the database.

    Args:
        db (AsyncSession): The database session to use for the update.
        customer_id (int): The ID of the customer to update.
        customer_update (CustomerUpdate): The updated customer information.

    Returns:
        Customer: The updated customer object.

    Raises:
        HTTPException: If the customer is not found or there is an error
                                                            during the update.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)
        await update_customer_helper(db_customer, customer_update)
        await db.commit()
        await db.refresh(db_customer)

        logger.info(f"Customer with ID {customer_id} updated successfully")
        return Customer.model_validate(db_customer)

    except NoResultFound:
        logger.error(f"Customer with ID {customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )

    except ValidationError as e:
        await db.rollback()
        logger.error(
            f"Validation error for customer with ID {customer_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {format_validation_error_msg(e)}",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            (
                "Database error while updating customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the customer",
        )

    except Exception as e:
        await db.rollback()
        logger.error(
            (
                "Unexpected error while updating customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def delete_customer_by_id(db: AsyncSession, customer_id: int) -> None:
    """
    Deletes a customer from the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        customer_id (int): The ID of the customer to delete.

    Raises:
        HTTPException: If the customer is not found or there is an error
                                                            during deletion.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)
        await db.delete(db_customer)
        await db.commit()

        logger.info(f"Customer with ID {customer_id} deleted successfully")

    except NoResultFound:
        logger.error(f"Customer with ID {customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            (
                "Database error while deleting customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the customer",
        )

    except Exception as e:
        await db.rollback()
        logger.error(
            (
                "Unexpected error while deleting customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def get_customer_order_count(db: AsyncSession, customer_id: int) -> int:
    """
    Count the number of orders for a specific customer.

    Args:
        db (AsyncSession): The database session to use for the query.
        customer_id (int): The ID of the customer whose order count is needed.

    Returns:
        int: The number of orders for the specified customer.

    Raises:
        HTTPException: If the customer is not found or there is an error
                                                        querying the database.
    """
    try:
        count_coroutine = await db.execute(
            select(DBOrder).filter(DBOrder.customer_id == customer_id)
        )
        count = len(count_coroutine.scalars().all())

        logger.info(
            (
                f"Order count for customer with ID {customer_id}"
                "retrieved successfully"
            )
        )
        return count

    except NoResultFound:
        logger.error(f"Customer with ID {customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )

    except SQLAlchemyError as e:
        logger.error(
            (
                "Database error while counting orders for customer with ID"
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while counting orders",
        )

    except Exception as e:
        logger.error(
            (
                "Unexpected error while counting orders for customer with ID "
                f"{customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


async def get_customer_recent_orders(
    db: AsyncSession, customer_id: int, limit: int
) -> CustomerOrders:
    """
    Retrieve a customer's most recent orders.

    Args:
        db (AsyncSession): The database session to use for the query.
        customer_id (int): The ID of the customer to fetch.
        limit (int): Number of recent orders to retrieve.

    Returns:
        CustomerOrders: Customer object including their recent orders.

    Raises:
        HTTPException: If the customer or orders cannot be retrieved.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)

        customer_orders_coroutine = await db.execute(
            select(DBOrder)
            .filter(DBOrder.customer_id == customer_id)
            .order_by(DBOrder.created_at.desc())
            .limit(limit)
        )
        customer_orders = customer_orders_coroutine.scalars().all()

        customer = CustomerOrders.model_validate(db_customer)
        customer.orders = [
            Order.model_validate(order) for order in customer_orders
        ]

        logger.info(
            (
                f"Retrieved {len(customer_orders)} "
                f"recent orders for customer with ID {customer_id}"
            )
        )
        return customer

    except NoResultFound:
        logger.error(f"Customer with ID {customer_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )

    except ValidationError as e:
        logger.error(
            f"Validation error for customer with ID {customer_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {format_validation_error_msg(e)}",
        )

    except SQLAlchemyError as e:
        logger.error(
            (
                "Database error while retrieving recent orders "
                f"for customer with ID {customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving recent orders",
        )

    except Exception as e:
        logger.error(
            (
                "Unexpected error while retrieving recent orders "
                f"for customer with ID {customer_id}: {e}"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
