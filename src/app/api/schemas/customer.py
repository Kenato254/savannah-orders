from datetime import datetime

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

from .order import Order

REGEX = r'^\+?[1-9]\d{9,14}$'


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: Annotated[
        str, StringConstraints(min_length=10, max_length=15, pattern=REGEX)
    ] = Field(...)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: Annotated[
        str | None,
        StringConstraints(min_length=10, max_length=15, pattern=REGEX),
    ] = None


class Customer(CustomerBase):
    id: int
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerOrders(Customer):
    orders: list[Order] = []
