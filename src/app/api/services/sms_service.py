import asyncio

from fastapi import BackgroundTasks

from ...settings.config import config
from ...settings.logging import logger
from ..schemas.customer import Customer
from ..schemas.order import OrderCreate


async def send_sms(sms_service, order: OrderCreate, customer: Customer):
    recipients = [customer.phone_number]

    message = f"""
    Hi {customer.name}!

    Your order of {order.quantity} x {order.item} has been placed.
    Total: ${order.amount*order.quantity:.2f}
    """.strip()

    sender = f"{config.AFRICASTALKING_CODE}"
    try:
        response = await asyncio.to_thread(
            sms_service.send, message, recipients, sender
        )
        logger.info(
            f"SMS sent successfully: {response["SMSMessageData"]["Message"]}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error sending SMS to {customer.phone_number}: {e}"
        )


async def send_sms_task(
    background_tasks: BackgroundTasks,
    sms_service,
    order: OrderCreate,
    customer: Customer,
):
    background_tasks.add_task(send_sms, sms_service, order, customer)
