from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models.customers import Customer
from ..schemas.order import OrderStatus
from .base_model import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"

    item = Column(String(length=100), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    status = Column(
        SQLEnum(OrderStatus), default=OrderStatus.ACTIVE, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped[Customer] = relationship("Customer")
