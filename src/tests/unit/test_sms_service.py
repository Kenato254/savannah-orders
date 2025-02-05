import datetime
import textwrap
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import BackgroundTasks

from src.app.api.schemas.customer import Customer
from src.app.api.schemas.order import OrderCreate
from src.app.api.services.sms_service import send_sms, send_sms_task
from src.app.settings.config import config


@pytest.fixture
def mock_sms_service():
    return MagicMock()


@pytest.fixture
def mock_logger():
    with patch("src.app.api.services.sms_service.logger") as mock:
        yield mock


@pytest.fixture
def mock_to_thread():
    with patch("asyncio.to_thread") as mock:
        yield mock


@pytest.fixture
def mock_order():
    mock_order_create = Mock(spec=OrderCreate)
    mock_order_create.item = "Test Item"
    mock_order_create.quantity = 1
    mock_order_create.amount = 10.0
    return mock_order_create


@pytest.fixture
def mock_customer():
    mock_customer_ = Mock(spec=Customer)
    mock_customer_.name = "Test Customer"
    mock_customer_.phone_number = "+1234567890"
    mock_customer_.code = "CUST001"
    mock_customer_.created_at = datetime.datetime.now(datetime.timezone.utc)
    mock_customer_.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return mock_customer_


@pytest.mark.asyncio
async def test_send_sms_success(
    mock_sms_service, mock_logger, mock_to_thread, mock_order, mock_customer
):
    mock_response = {"SMSMessageData": {"Message": "SMS sent"}}
    mock_to_thread.return_value = mock_response

    # Calculate the total amount before formatting the string
    total_amount = mock_order.amount * mock_order.quantity

    # Use .format with calculated value
    expected_message = (
        textwrap.dedent(
            """
            Hi {customer.name}!

                Your order of {order.quantity} x {order.item} has been placed.
                Total: ${total_amount:.2f}
            """
        )
        .strip()
        .format(
            customer=mock_customer, order=mock_order, total_amount=total_amount
        )
    )

    await send_sms(mock_sms_service, mock_order, mock_customer)

    mock_to_thread.assert_called_once_with(
        mock_sms_service.send,
        expected_message,
        [mock_customer.phone_number],
        f"{config.AFRICASTALKING_CODE}",
    )
    mock_logger.info.assert_called_once_with(
        f"SMS sent successfully: {mock_response['SMSMessageData']['Message']}"
    )


@pytest.mark.asyncio
async def test_send_sms_failure(
    mock_sms_service, mock_logger, mock_to_thread, mock_order, mock_customer
):
    mock_to_thread.side_effect = Exception("SMS Service Down")

    await send_sms(mock_sms_service, mock_order, mock_customer)

    mock_to_thread.assert_called_once()
    mock_logger.error.assert_called_once_with(
        (
            "Unexpected error sending SMS to"
            f" {mock_customer.phone_number}: SMS Service Down"
        )
    )


@pytest.mark.asyncio
async def test_send_sms_task(mock_sms_service, mock_order, mock_customer):

    background_tasks = BackgroundTasks()

    await send_sms_task(
        background_tasks, mock_sms_service, mock_order, mock_customer
    )

    assert len(background_tasks.tasks) == 1
    task = background_tasks.tasks[0]
    assert task.func.__name__ == "send_sms"
    assert task.args == (mock_sms_service, mock_order, mock_customer)
