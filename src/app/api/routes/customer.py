from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.schemas.token import TokenData

from ..auth.oidc import get_current_user, has_role
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

# Initialize `Customer` Routes
router = APIRouter()


@router.post(
    "/",
    summary="Create new customer associated to a user",
    status_code=201,
    dependencies=[Depends(has_role("user"))],
)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user),
) -> Customer:
    return await insert_customer(db, customer, user_id=token_data.sub)


@router.get(
    "/{id}",
    summary="Retrieve a customer by id",
    response_model=Customer,
    dependencies=[Depends(has_role("user"))],
)
async def get_customer(
    id: Annotated[int, Path(title="The ID of the customer to retrieve")],
    db: AsyncSession = Depends(get_db),
) -> Customer:
    return await get_customer_by_id(db, id)


@router.get(
    "/",
    summary="Retrieve all customers.",
    response_model=list[Customer],
    dependencies=[Depends(has_role("admin"))],
)
async def get_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
) -> list[Customer]:
    return await get_all_customers(db, skip, limit)


@router.patch(
    "/{id}",
    summary="Update a customer by id",
    response_model=Customer,
    dependencies=[Depends(has_role("user"))],
)
async def update_customer(
    customer_update: CustomerUpdate,
    id: Annotated[int, Path(title="The ID of the customer to retrieve")],
    db: AsyncSession = Depends(get_db),
) -> Customer:
    return await update_customer_by_id(db, id, customer_update)


@router.delete(
    "/{id}",
    summary="Delete a customer by id",
    status_code=204,
    dependencies=[Depends(has_role("user"))],
)
async def delete_customer(
    id: Annotated[int, Path(title="The ID of the customer to retrieve")],
    db: AsyncSession = Depends(get_db),
) -> None:
    await delete_customer_by_id(db, id)


@router.get(
    "/{id}/orders/count",
    summary="Retrieve customer orders count",
    response_model=int,
    dependencies=[Depends(has_role("user"))],
)
async def get_customer_order_count(
    id: Annotated[int, Path(title="The ID of the customer to retrieve")],
    db: AsyncSession = Depends(get_db),
) -> int:
    return await retrieve_customer_order_count(db, id)


@router.get(
    "/{id}/orders/recent",
    summary="Retrieve customer recent orders",
    response_model=CustomerOrders,
    dependencies=[Depends(has_role("user"))],
)
async def get_customer_recent_order(
    id: Annotated[int, Path(title="The ID of the customer to retrieve")],
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await retrieve_customer_recent_orders(db, id, limit)
