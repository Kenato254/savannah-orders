from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..utils.customer_utils import update_customer_helper
from ..models.customers import Customer as DBCustomer
from ..schemas.customer import Customer, CustomerCreate, CustomerUpdate
from ..utils.error_handler import handle_error_helper
from ..utils.code_generator import generate_cust_code


def create_customer(db: Session, customer: CustomerCreate) -> None:
    try:
        db_customer = DBCustomer(
            name=customer.name, phone_number=customer.phone_number
        )

        code = generate_cust_code(customer.id)  # type: ignore
        db_customer.code = code  # type: ignore
        db.add(customer)
        db.commit()
        db.refresh(db_customer)
    except SQLAlchemyError as e:
        handle_error_helper(
            500, f"Error creating a customer {e.with_traceback}"
        )


def get_customer_by_id(  # type: ignore
    db: Session, customer_id: int
) -> Customer:
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
        db_user = (
            db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
        )
        if not db_user:
            handle_error_helper(
                404, f"Customer with id: {customer_id} does not exist"
            )
        return Customer.model_validate(db_user)
    except SQLAlchemyError as e:
        handle_error_helper(
            500,
            (
                "Error reading customer with id:"
                f"{customer_id}. Error {e.with_traceback}"
            ),
        )


def get_customers(db: Session, skip: int, limit: int = 10) -> list[Customer]:
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


def update_customer(
    db: Session, customer_id: int, customer_update: CustomerUpdate
) -> None:
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
        db_user = get_customer_by_id(db, customer_id)
        update_customer_helper(db_user, customer_update)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError as e:
        db.rollback()
        handle_error_helper(
            500,
            (
                "Error updating user with id:"
                f"{customer_id}. Error {e.with_traceback}"
            ),
        )


def delete_customer(db: Session, customer_id: int) -> None:
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
        db_user = get_customer_by_id(db, customer_id)
        db.delete(db_user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        handle_error_helper(
            500,
            (
                "Error deleting user with id:"
                f"{customer_id}. Error {e.with_traceback}"
            ),
        )
