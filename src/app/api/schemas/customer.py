from datetime import datetime

from pydantic import BaseModel

from .order import Order


class CustomerBase(BaseModel):
    name: str
    phone_number: str


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None


class Customer(CustomerBase):
    id: int
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerOrders(Customer):
    orders: list[Order] = []
