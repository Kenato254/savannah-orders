from typing import Annotated
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from ..services.customer_service import (
    delete_customer_by_id,
    get_customer_by_id,
    insert_customer,
    get_all_customers,
    update_customer_by_id,
)
from ..db.session import get_db
from ..schemas.customer import Customer, CustomerCreate, CustomerUpdate

# Initialize Customer Route
router = APIRouter()


@router.post("/", summary="Create new customer", status_code=201)
async def create_customer(
    customer: CustomerCreate, db: Session = Depends(get_db)
) -> None:
    """
    Create a new customer.
    """
    insert_customer(db, customer)


@router.get(
    "/{id}",
    summary="Retrieve a customer by id",
    response_model=Customer,
)
async def get_customer(
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: Session = Depends(get_db),
) -> Customer:
    """Retrieve customer by id"""
    return get_customer_by_id(db, id)


@router.get(
    "/",
    summary="Retrieve all customers based on pagination",
    response_model=list[Customer],
)
async def get_users(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
) -> list[Customer]:
    """
    Retrieves all customers based on pagination.
    """
    return get_all_customers(db, skip, limit)


@router.patch(
    "/{id}",
    summary="Update a customer by id",
    response_model=Customer,
)
async def update_customer(
    customer_update: CustomerUpdate,
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: Session = Depends(get_db),
) -> Customer:
    """Update customer by id"""
    return update_customer_by_id(db, id, customer_update)


@router.delete("/{id}", summary="Delete a customer by id", status_code=204)
async def delete_customer(
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: Session = Depends(get_db),
) -> None:
    """Delete customer by id"""
    delete_customer_by_id(db, id)
