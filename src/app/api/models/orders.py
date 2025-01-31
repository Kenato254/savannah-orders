from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from ..schemas.order import OrderStatus
from .base_model import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    status = Column(SQLEnum, default=OrderStatus.ACTIVE, nullable=False)
    customer = relationship("Customer")
