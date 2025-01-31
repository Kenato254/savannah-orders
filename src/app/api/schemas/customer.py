from datetime import datetime
from pydantic import BaseModel


class CustomerBase(BaseModel):
    name: str
    phone_number: str


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    code: str | None = None


class Customer(CustomerBase):
    id: int
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
