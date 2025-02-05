import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.models.customer import Customer
from src.app.api.models.order import Order as DBOrder
from src.app.api.schemas.order import OrderCreate, OrderStatus
from src.app.api.services.order_service import (
    delete_order_by_id,
    get_all_orders,
    get_order_by_id,
    get_orders_by_customer_id,
    insert_order,
    update_order_by_id,
)


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_db_order():
    mock_order = MagicMock(spec=DBOrder)
    mock_order.id = 1
    mock_order.item = "test-item"
    mock_order.amount = 100.0
    mock_order.status = OrderStatus.ACTIVE
    mock_order.customer_id = 1
    mock_order.created_at = datetime.datetime.now(datetime.timezone.utc)
    mock_order.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return mock_order


@pytest.fixture
def mock_db_customer():
    mock_customer = MagicMock(spec=Customer)
    mock_customer.id = 1
    mock_customer.name = "John Doe"
    mock_customer.phone_number = "+25475486253"
    mock_customer.code = "CUST001"
    mock_customer.created_at = datetime.datetime.now(datetime.timezone.utc)
    mock_customer.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return mock_customer


@pytest.fixture
def mock_background_task():
    return MagicMock(spec=BackgroundTasks)


@pytest.fixture
def mock_sms_service():
    return MagicMock()


@pytest.mark.asyncio
async def test_when_insert_order_is_success(
    mock_db,
    mock_db_order,
    mock_db_customer,
    mock_background_task,
    mock_sms_service,
):
    # Test data setup
    order_create = OrderCreate(
        item="test-item", amount=100.0, customer_id=mock_db_customer.id
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_customer
    mock_db.execute = AsyncMock(side_effect=mock_result)

    with patch(
        "src.app.api.schemas.order.Order.model_validate"
    ) as mock_model_validate_order:
        with patch(
            "src.app.api.schemas.customer.Customer.model_validate"
        ) as mock_model_validate_customer:
            with patch(
                "src.app.api.utils.customer._get_customer_by_id"
            ) as mock_utils_get_customer:
                mock_utils_get_customer.return_value = mock_db_customer

                mock_model_validate_order.return_value = mock_db_order

                mock_model_validate_customer.return_value = mock_db_customer

                result = await insert_order(
                    mock_db,
                    order_create,
                    mock_background_task,
                    mock_sms_service,
                )

                assert result.item == order_create.item
                assert result.amount == order_create.amount
                assert result.customer_id == mock_db_customer.id

                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_when_insert_order_is_failure(
    mock_db, mock_background_task, mock_sms_service
):
    order_create = OrderCreate(item="test-item", amount=100.0, customer_id=1)

    mock_db.execute = AsyncMock(side_effect=MagicMock())
    mock_db.add.side_effect = SQLAlchemyError("Database Error")

    with pytest.raises(HTTPException):
        await insert_order(
            mock_db, order_create, mock_background_task, mock_sms_service
        )
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_order_id_is_success(mock_db, mock_db_order):
    order_id = 1

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_db_order

    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "src.app.api.schemas.order.Order.model_validate"
    ) as mock_model_validate:
        mock_model_validate.return_value = mock_db_order

        with patch(
            "src.app.api.utils.order._get_order_by_id"
        ) as mock_utils_get_order:
            mock_utils_get_order.return_value = mock_db_order

            result = await get_order_by_id(mock_db, order_id)

            assert result.item == mock_db_order.item
            assert result.amount == mock_db_order.amount
            assert result.status == mock_db_order.status

        mock_db.execute.assert_awaited_once()
        mock_result.scalars.assert_called_once()
        mock_result.scalars.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_order_id_is_failure(mock_db):
    order_id = 1
    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await get_order_by_id(mock_db, order_id)
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_order_id_is_not_found(mock_db):
    order_id = 1

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None

    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException):
        await get_order_by_id(mock_db, order_id)

    mock_db.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_result.scalars.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_all_orders_is_success(mock_db, mock_db_order):
    expected_orders = [mock_db_order, mock_db_order, mock_db_order]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_orders

    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "src.app.api.schemas.order.Order.model_validate"
    ) as mock_model_validate:
        mock_model_validate.side_effect = lambda order: order

        result = await get_all_orders(mock_db, 0, 3)

        assert result == expected_orders
        mock_db.execute.assert_awaited_once()
        mock_result.scalars.assert_called_once()
        mock_result.scalars.return_value.all.assert_called_once()
        assert mock_model_validate.call_count == len(expected_orders)


@pytest.mark.asyncio
async def test_when_get_all_orders_is_failure(mock_db):
    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await get_all_orders(mock_db)
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_orders_by_customer_id_is_not_found(mock_db):
    order_id = 1

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None

    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException):
        await get_order_by_id(mock_db, order_id)

    mock_db.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_result.scalars.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_when_get_orders_by_customer_id_is_failure(mock_db):
    customer_id = 1

    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await get_orders_by_customer_id(db=mock_db, customer_id=customer_id)

    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_when_update_order_by_id_is_success(mock_db, mock_db_order):
    order_id = 1
    new_status = OrderStatus.CANCELLED

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_db_order
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Mock the update_time function
    with patch(
        "src.app.api.services.order_service.update_time",
        new_callable=AsyncMock,
    ) as mock_update_time:
        with patch(
            "src.app.api.schemas.order.Order.model_validate"
        ) as mock_model_validate:
            mock_model_validate.return_value = mock_db_order

            result = await update_order_by_id(mock_db, order_id, new_status)

            assert result.status == new_status
            mock_db.execute.assert_awaited_once()
            mock_update_time.assert_awaited_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_when_update_order_by_id_is_failure(mock_db):
    order_id = 1
    new_status = OrderStatus.CANCELLED

    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await update_order_by_id(mock_db, order_id, new_status)
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_when_delete_order_by_id_is_success(mock_db, mock_db_order):
    order_id = 1

    mock_result = MagicMock()
    mock_result.scalars.return_value.first_return_value = mock_db_order
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "src.app.api.services.order_service._get_order_by_id",
        return_value=mock_db_order,
    ) as mock_get_order:
        with patch(
            "src.app.api.services.order_service.handle_error_helper"
        ) as mock_error_handler:
            await delete_order_by_id(mock_db, order_id)

            mock_get_order.assert_awaited_once_with(mock_db, order_id)
            mock_db.delete.assert_called_once_with(mock_db_order)
            mock_db.commit.assert_called_once()
            mock_error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_when_delete_order_by_id_is_failure(mock_db):
    order_id = 1

    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException):
        await delete_order_by_id(mock_db, order_id)

    mock_db.execute.assert_called_once()
