from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ...settings.sms.init import get_sms_service
from ..auth.oidc import has_role
from ..db.session import get_db
from ..schemas.order import Order, OrderCreate, OrderStatus
from ..services.order_service import (
    delete_order_by_id,
    get_all_orders,
    get_order_by_id,
    get_orders_by_customer_id,
    insert_order,
    update_order_by_id,
)

# Intialize `Order` Routes
router = APIRouter()


@router.post(
    "/",
    response_model=Order,
    status_code=201,
    summary="Customers can create a new order. ",
    dependencies=[Depends(has_role("user"))],
)
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    sms_service=Depends(get_sms_service),
):
    return await insert_order(db, order, background_tasks, sms_service)


@router.get(
    "/{order_id}/",
    response_model=Order,
    summary="Customers can retrieve an order by its id",
    dependencies=[Depends(has_role("user"))],
)
async def read_order(
    order_id: Annotated[int, Path(title="The ID of the order to retrieve")],
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_order_by_id(db, order_id)
    except HTTPException as e:
        raise e


@router.get(
    "/",
    response_model=list[Order],
    summary="Admin can retrieve all orders existing in the database ",
    dependencies=[Depends(has_role("admin"))],
)
async def read_orders(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await get_all_orders(db, skip, limit)


@router.get(
    "/customers/{customer_id}/orders",
    response_model=list[Order],
    summary="Customers can retrieve all orders associated to them",
    dependencies=[Depends(has_role("user"))],
)
async def read_customer_orders(
    customer_id: Annotated[
        int, Path(title="The ID of the customer to retrieve")
    ],
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await get_orders_by_customer_id(db, customer_id, skip, limit)


@router.put(
    "/{order_id}",
    response_model=Order,
    summary="Customers can update an order by its id",
    dependencies=[Depends(has_role("user"))],
)
async def update_order(
    order_id: Annotated[int, Path(title="The ID of the order to retrieve")],
    order: OrderStatus,
    db: AsyncSession = Depends(get_db),
) -> Order:
    try:
        return await update_order_by_id(db, order_id, order)
    except HTTPException as e:
        raise e


@router.delete(
    "/{order_id}",
    status_code=204,
    summary="Customers can delete an order by its id if in `Pending` state ",
    dependencies=[Depends(has_role("admin"))],
)
async def delete_order(
    order_id: Annotated[int, Path(title="The ID of the order to retrieve")],
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await delete_order_by_id(db, order_id)
    except HTTPException as e:
        raise e
