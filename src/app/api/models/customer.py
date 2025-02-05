from sqlalchemy import Column, String

from .base_model import BaseModel


class Customer(BaseModel):
    __tablename__ = "customers"

    name = Column(String(length=100), nullable=False)
    code = Column(String(length=50), nullable=True)
    phone_number = Column(String(length=20), nullable=False)
