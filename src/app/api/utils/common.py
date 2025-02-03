import datetime

from ..models.order import Order


async def update_time(order: Order) -> None:
    order.updated_at = datetime.datetime.now(datetime.timezone.utc)
