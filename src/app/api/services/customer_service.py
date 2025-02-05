from pydantic_core import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
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
from ..utils.code_generator import generate_code
from ..utils.customer import _get_customer_by_id, update_customer_helper
from ..utils.error_handler import handle_error_helper


async def insert_customer(db: AsyncSession, customer: CustomerCreate) -> None:
    """
    Inserts a new customer into the database.

    Args:
        db (Session): The database session to use for the operation.
        customer (CustomerCreate): The customer data to insert.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there is an error during the database operation.

    """
    try:
        db_customer = DBCustomer(
            name=customer.name, phone_number=customer.phone_number
        )
        db.add(db_customer)
        await db.flush()

        code = await generate_code(int(db_customer.id))  # type: ignore
        db_customer.code = code
        await db.commit()
        await db.refresh(db_customer)

        logger.info("Customer created successfully")
    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(500, f"Error creating a customer {e}")
        raise


async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Customer:
    """
    Retrieve a customer by their ID from the database.

    Args:
        db (Session): The database session to use for the query.
        customer_id (int): The ID of the customer to retrieve.

    Returns:
        Customer: The customer object if found.

    Raises:
        HTTPException: If the customer with the given ID does not exist.
        HTTPException: If there is an error reading the customer from the
                                                                database.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)
        logger.info("Customer retrieved successfully")
        return Customer.model_validate(db_customer)

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(
            400, f"Error reading customer with id: {customer_id}. Error {e}"
        )
        raise

    except SQLAlchemyError as e:
        handle_error_helper(
            500, f"Error reading customer with id: {customer_id}. Error {e}"
        )
        raise


async def get_all_customers(
    db: AsyncSession, skip: int, limit: int
) -> list[Customer]:
    """
    Retrieve a list of customers from the database with pagination.

    Args:
        db (Session): The database session to use for the query.
        skip (int): The number of records to skip before starting to collect
                                                                the result set.
        limit (int): The maximum number of records to return. Defaults to 10.

    Returns:
        list[Customer]: A list of Customer objects.

    Raises:
        SQLAlchemyError: If there is an error querying the database.
    """
    try:
        customers_query = await db.execute(
            select(DBCustomer).offset(skip).limit(limit)
        )
        customers = customers_query.scalars().all()

        logger.info("Customers retrieved successfully")
        return [Customer.model_validate(customer) for customer in customers]

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(400, f"Error reading customers: {e}")
        raise

    except SQLAlchemyError as e:
        handle_error_helper(500, f"Error reading customers. Error {e}")
        raise


async def update_customer_by_id(
    db: AsyncSession, customer_id: int, customer_update: CustomerUpdate
) -> Customer:
    """
    Update a customer's information in the database.

    Args:
        db (Session): The database session to use for the update.
        customer_id (int): The ID of the customer to update.
        customer_update (CustomerUpdate): The updated customer information.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there is an error during the update process.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)
        await update_customer_helper(db_customer, customer_update)
        await db.commit()
        await db.refresh(db_customer)

        logger.info("Customer updated successfully")
        return Customer.model_validate(db_customer)

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(
            400, f"Error updating customer with id: {customer_id}. Error {e}"
        )
        raise

    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(
            500, f"Error updating customer with id: {customer_id}. Error {e}"
        )
        raise


async def delete_customer_by_id(db: AsyncSession, customer_id: int) -> None:
    """
    Deletes a customer from the database.

    Args:
        db (Session): The database session to use for the operation.
        customer_id (int): The ID of the customer to delete.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there is an error during the deletion process,
                         the transaction is rolled back and an error is logged.
    """
    try:
        db_customer = await _get_customer_by_id(db, customer_id)
        await db.delete(db_customer)
        await db.commit()

        logger.info("Customer deleted successfully")
    except SQLAlchemyError as e:
        await db.rollback()
        handle_error_helper(
            500,
            ("Error deleting customer with id:" f"{customer_id}. Error {e}"),
        )
        raise


async def get_customer_order_count(db: AsyncSession, customer_id: int) -> int:
    """
    Count the number of orders for a specific customer.

    Args:
        db (Session): The database session to use for the query.
        customer_id (int): The ID of the customer whose order count is needed.

    Returns:
        int: The number of orders for the specified customer.

    Raises:
        HTTPException: If there is an error querying the database.
    """
    try:
        count_coroutine = await db.execute(
            select(DBOrder).filter(DBOrder.customer_id == customer_id)
        )
        count = len(count_coroutine.scalars().all())

        logger.info("Customer order count retrieved successfully")
        return count
    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            (
                "Error counting orders for customer"
                f" {customer_id}. Error {e}"
            ),
        )
        raise


async def get_customer_recent_orders(
    db: AsyncSession, customer_id: int, limit: int
) -> CustomerOrders:
    """
    Retrieve a customer most recent orders.

    Args:
        db (Session): The database session to use for the query.
        customer_id (int): The ID of the customer to fetch.
        limit (int, optional): Number of recent orders to retrieve.
                                                        Defaults to 5.

    Returns:
        Customer: Customer object including their recent orders.

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

        return customer

    except ValidationError as e:
        await db.rollback()
        handle_error_helper(
            400,
            ("Error reading customer with id:" f"{customer_id}. Error {e}"),
        )
        raise

    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            (
                "Error reading customer with recent orders for id:"
                f"{customer_id}. Error {e}"
            ),
        )
        raise
