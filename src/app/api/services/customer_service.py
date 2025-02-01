from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..utils.customer_utils import update_customer_helper
from ..models.customers import Customer as DBCustomer
from ..schemas.customer import Customer, CustomerCreate, CustomerUpdate
from ..utils.error_handler import handle_error_helper
from ..utils.code_generator import generate_cust_code


def insert_customer(db: Session, customer: CustomerCreate) -> None:
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
        db.flush()

        code = generate_cust_code(db_customer.id)  # type: ignore
        db_customer.code = code  # type: ignore
        db.commit()
        db.refresh(db_customer)
    except SQLAlchemyError as e:
        handle_error_helper(
            500, f"Error creating a customer {e.with_traceback}"
        )


def get_customer_by_id(  # type: ignore
    db: Session, customer_id: int
) -> DBCustomer:
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
        db_customer = (
            db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
        )
        if db_customer is None:
            handle_error_helper(
                404, f"Customer with id: {customer_id} does not exist"
            )
        return db_customer  # type: ignore
    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            (
                "Error reading customer with id:"
                f"{customer_id}. Error {e.with_traceback}"
            ),
        )


def get_all_customers(db: Session, skip: int, limit: int) -> list[Customer]:
    """
    Retrieve a list of customers from the database with pagination.

    Args:
        db (Session): The database session to use for the query.
        skip (int): The number of records to skip before starting to collect
                                                                the result set.
        limit (int, optional): The maximum number of records to return.
                                                                Defaults to 10.

    Returns:
        list[Customer]: A list of Customer objects.

    Raises:
        SQLAlchemyError: If there is an error querying the database.
    """
    try:
        customers = db.query(DBCustomer).offset(skip).limit(limit).all()
        return [Customer.model_validate(customer) for customer in customers]
    except SQLAlchemyError as e:
        handle_error_helper(
            500, f"Error reading customers. Error {e.with_traceback}"
        )
        return []


def update_customer_by_id(  # type: ignore
    db: Session, customer_id: int, customer_update: CustomerUpdate
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
        db_customer = get_customer_by_id(db, customer_id)
        update_customer_helper(db_customer, customer_update)
        db.commit()
        db.refresh(db_customer)
        return Customer.model_validate(db_customer)
    except SQLAlchemyError as e:
        db.rollback()
        handle_error_helper(
            500,
            (
                "Error updating customer with id:"
                f"{customer_id}. Error {e.with_traceback}"
            ),
        )


def delete_customer_by_id(db: Session, customer_id: int) -> None:
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
        db_customer = get_customer_by_id(db, customer_id)
        db.delete(db_customer)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        handle_error_helper(
            500,
            (
                "Error deleting customer with id:"
                f"{customer_id}. Error {e.with_traceback}"
            ),
        )
