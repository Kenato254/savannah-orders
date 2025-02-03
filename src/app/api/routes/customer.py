from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..schemas.customer import (
    Customer,
    CustomerCreate,
    CustomerOrders,
    CustomerUpdate,
)
from ..services.customer_service import (
    delete_customer_by_id,
    get_all_customers,
    get_customer_by_id,
)
from ..services.customer_service import (
    get_customer_order_count as retrieve_customer_order_count,
)
from ..services.customer_service import (
    get_customer_recent_orders as retrieve_customer_recent_orders,
)
from ..services.customer_service import (
    insert_customer,
    update_customer_by_id,
)

# Initialize Customer Route
router = APIRouter()


@router.post("/", summary="Create new customer", status_code=201)
async def create_customer(
    customer: CustomerCreate, db: AsyncSession = Depends(get_db)
) -> None:
    """
    Create a new customer.
    """
    await insert_customer(db, customer)


@router.get(
    "/{id}", summary="Retrieve a customer by id", response_model=Customer
)
async def get_customer(
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: AsyncSession = Depends(get_db),
) -> Customer:
    """Retrieve customer by id"""
    return await get_customer_by_id(db, id)


@router.get(
    "/",
    summary="Retrieve all customers based on pagination",
    response_model=list[Customer],
)
async def get_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
) -> list[Customer]:
    """
    Retrieves all customers based on pagination.
    """
    return await get_all_customers(db, skip, limit)


@router.patch(
    "/{id}", summary="Update a customer by id", response_model=Customer
)
async def update_customer(
    customer_update: CustomerUpdate,
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: AsyncSession = Depends(get_db),
) -> Customer:
    """Update customer by id"""
    return await update_customer_by_id(db, id, customer_update)


@router.delete("/{id}", summary="Delete a customer by id", status_code=204)
async def delete_customer(
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete customer by id"""
    await delete_customer_by_id(db, id)


@router.get(
    "/{id}/orders/count",
    summary="Retrieve customer orders count",
    response_model=int,
)
async def get_customer_order_count(
    id: Annotated[int, Path(title="The ID of the customer to get")],
    db: AsyncSession = Depends(get_db),
) -> int:
    """Retrieve customer orders count"""
    return await retrieve_customer_order_count(db, id)


@router.get(
    "/{id}/orders/recent",
    summary="Retrieve customer recent orders",
    response_model=CustomerOrders,
)
async def get_customer_recent_order(
    id: Annotated[int, Path(title="The ID of the customer to get")],
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve customer recent orders"""
    return await retrieve_customer_recent_orders(db, id, limit)
