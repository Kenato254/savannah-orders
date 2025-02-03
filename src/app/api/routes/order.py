from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.db.session import get_db
from src.app.api.schemas.order import Order, OrderCreate, OrderStatus
from src.app.api.services.order_service import (
    delete_order_by_id,
    get_all_orders,
    get_order_by_id,
    get_orders_by_customer_id,
    insert_order,
    update_order_by_id,
)

router = APIRouter()


@router.post("/", response_model=Order)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await insert_order(db, order)


@router.get("/{order_id}/", response_model=Order)
async def read_order(order_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await get_order_by_id(db, order_id)
    except HTTPException as e:
        raise e


@router.get("/", response_model=list[Order])
async def read_orders(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await get_all_orders(db, skip, limit)


@router.get("/customers/{customer_id}/", response_model=list[Order])
async def read_customer_orders(
    customer_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await get_orders_by_customer_id(db, customer_id, skip, limit)


@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: int, order: OrderStatus, db: AsyncSession = Depends(get_db)
):
    try:
        return await update_order_by_id(db, order_id, order)
    except HTTPException as e:
        raise e


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await delete_order_by_id(db, order_id)
    except HTTPException as e:
        raise e
