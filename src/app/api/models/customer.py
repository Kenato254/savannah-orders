from sqlalchemy import Column, Integer, String

from .base_model import BaseModel


class Customer(BaseModel):
    __tablename__ = "customers"

    name = Column(String(length=100), nullable=False)
    user_id = Column(String(length=100), nullable=False, unique=True)
    code = Column(Integer, nullable=False)
    phone_number = Column(String(length=20), nullable=False)
