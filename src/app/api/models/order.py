from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..schemas.order import OrderStatus
from .base_model import BaseModel
from .customer import Customer


class Order(BaseModel):
    __tablename__ = "orders"

    item = Column(String(length=100), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(
        SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped[Customer] = relationship("Customer")
