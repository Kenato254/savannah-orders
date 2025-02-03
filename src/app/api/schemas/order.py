from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class OrderStatus(str, Enum):
    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    DELIVERED = "Delivered"


class OrderBase(BaseModel):
    item: str
    amount: float
    customer_id: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: OrderStatus


class Order(OrderBase):
    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
