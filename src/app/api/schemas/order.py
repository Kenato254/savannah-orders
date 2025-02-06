from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    DELIVERED = "Delivered"


class OrderBase(BaseModel):
    item: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)
    customer_id: int = Field(..., gt=0)


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
