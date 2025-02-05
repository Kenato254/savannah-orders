import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.models.customer import Customer as DBCustomer
from src.app.api.models.order import Order
from src.app.api.schemas.customer import CustomerCreate, CustomerUpdate
from src.app.api.schemas.order import OrderStatus
from src.app.api.services.customer_service import (
    delete_customer_by_id,
    get_all_customers,
    get_customer_by_id,
    get_customer_order_count,
    insert_customer,
    update_customer_by_id,
)
from src.app.api.utils.code_generator import generate_code
from src.app.api.utils.customer import _get_customer_by_id
from src.app.api.utils.error_handler import handle_error_helper


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_db_customer():
    mock_customer = MagicMock(spec=DBCustomer)
    mock_customer.id = 1
    mock_customer.name = "John Doe"
    mock_customer.phone_number = "1234567890"
    mock_customer.code = "CUST001"
    mock_customer.created_at = datetime.datetime.now(datetime.timezone.utc)
    mock_customer.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return mock_customer


@pytest.fixture
def mock_db_order():
    mock_order = MagicMock(spec=Order)
    mock_order.id = 1
    mock_order.item = "test-item"
    mock_order.amount = 100.0
    mock_order.status = OrderStatus.ACTIVE
    mock_order.customer_id = 1
    mock_order.created_at = datetime.datetime.now(datetime.timezone.utc)
    mock_order.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return mock_order


@pytest.mark.asyncio
async def test_when_insert_customer_is_success(mock_db, mock_db_customer):
    customer_data = CustomerCreate(name="John Doe", phone_number="1234567890")

    with (
        patch(
            "src.app.api.services.customer_service.DBCustomer",
            return_value=mock_db_customer,
        ),
        patch(
            "src.app.api.services.customer_service.generate_code",
            return_value="CUST1-250203-abcdefg",
        ),
    ):
        mock_db.add.return_value = None
        mock_db.flush.return_value = None
        await insert_customer(mock_db, customer_data)

    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_when_insert_customer_is_failure(mock_db):
    customer_data = CustomerCreate(name="John Doe", phone_number="1234567890")
    mock_db.add.side_effect = SQLAlchemyError("Database Error")

    with (
        pytest.raises(SQLAlchemyError),
        patch(
            "src.app.api.services.customer_service.handle_error_helper"
        ) as mock_handle_error,
    ):
        await insert_customer(mock_db, customer_data)

    mock_handle_error.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_customer_by_id_is_success(mock_db, mock_db_customer):
    customer_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_customer

    mock_db.execute = AsyncMock(return_value=mock_result)

    await _get_customer_by_id(mock_db, customer_id)

    mock_db.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_customer_by_id_is_not_found(mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with (
        pytest.raises(HTTPException),
        patch(
            "src.app.api.services.customer_service.handle_error_helper"
        ) as mock_handle_error,
    ):
        await get_customer_by_id(mock_db, 1)
        mock_handle_error.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_all_customers_is_success(mock_db, mock_db_customer):
    expected = [mock_db_customer, mock_db_customer, mock_db_customer]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "src.app.api.schemas.customer.Customer.model_validate"
    ) as mock_model_validate:
        mock_model_validate.side_effect = lambda customer: customer

        result = await get_all_customers(mock_db, 0, 3)

        assert result == expected

    mock_db.execute.assert_called_once()
    mock_result.scalars.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_all_customers_is_failure(mock_db):
    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await get_all_customers(mock_db, 0, 3)

    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_when_update_customer_by_id_is_success(
    mock_db, mock_db_customer
):
    customer_id = 1
    customer_update = CustomerUpdate(
        name="test customer", phone_number="+254722123123"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_customer
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "src.app.api.utils.customer.update_customer_helper"
    ) as mock_update_customer_helper:
        mock_update_customer_helper.return_value = mock_db_customer

        await update_customer_by_id(mock_db, customer_id, customer_update)

    mock_db.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_when_update_customer_by_id_is_failure(mock_db):
    customer_id = 1
    customer_update = CustomerUpdate(
        name="test customer", phone_number="+254722123123"
    )

    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await update_customer_by_id(mock_db, customer_id, customer_update)

    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_when_update_customer_by_id_is_not_found(mock_db):
    customer_id = 1
    customer_update = CustomerUpdate(
        name="test customer", phone_number="+254722123123"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException):

        await update_customer_by_id(mock_db, customer_id, customer_update)

    mock_db.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_when_delete_customer_by_id_is_success(
    mock_db, mock_db_customer
):
    customer_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_customer

    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "src.app.api.services.customer_service._get_customer_by_id",
        return_value=mock_db_customer,
    ) as mock_get_customer:
        with patch(
            "src.app.api.utils.error_handler.handle_error_helper"
        ) as mock_error_handler:
            await delete_customer_by_id(mock_db, customer_id)

            mock_get_customer.assert_awaited_once_with(mock_db, customer_id)
            mock_db.delete.assert_called_once_with(mock_db_customer)
            mock_db.commit.assert_called_once()
            mock_error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_when_delete_customer_by_id_is_failure(
    mock_db, mock_db_customer
):
    customer_id = 1

    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        with patch(
            "src.app.api.utils.error_handler.handle_error_helper"
        ) as mock_error_handler:
            await delete_customer_by_id(mock_db, customer_id)

            mock_db.delete.assert_called_once_with(mock_db_customer)
            mock_db.commit.assert_called_once()
            mock_error_handler.assert_called_once()


@pytest.mark.asyncio
async def test_when_delete_customer_by_id_is_not_found(mock_db):
    customer_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException):
        with patch(
            "src.app.api.utils.error_handler.handle_error_helper"
        ) as mock_error_handler:
            await delete_customer_by_id(mock_db, customer_id)

            mock_db.delete.assert_not_called()
            mock_db.commit.assert_not_called()
            mock_error_handler.assert_called_once()
    mock_db.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_when_generate_code():
    customer_id = "1"
    code = await generate_code(customer_id)
    assert code.startswith("CUST")
    assert len(code) == 21


@pytest.mark.asyncio
async def test_get_customer_order_count_is_success(mock_db, mock_db_order):
    expected = [
        mock_db_order,
        mock_db_order,
        mock_db_order,
        mock_db_order,
        mock_db_order,
    ]
    customer_id = 1
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_customer_order_count(mock_db, customer_id)

    assert result == len(expected)
    mock_db.execute.assert_called_once()
    mock_result.scalars.assert_called_once()
    mock_result.scalars.return_value.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_customer_order_count_is_failure(mock_db):
    customer_id = 1

    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        with patch(
            "src.app.api.utils.error_handler.handle_error_helper"
        ) as mock_error_handler:

            await get_customer_order_count(mock_db, customer_id)
            mock_error_handler.assert_called_once()

    mock_db.execute.assert_called_once()
    mock_db.execute.return_value.scalars.assert_not_called()
    mock_db.execute.return_value.scalars.return_value.all.assert_not_called()


def test_handle_error_helper():
    with patch("src.app.settings.logging.logger.error") as mock_logger:
        with pytest.raises(HTTPException) as e:
            handle_error_helper(404, "Not Found")
        assert e.value.status_code == 404
        mock_logger.assert_called_once_with("Error 404: Not Found")
