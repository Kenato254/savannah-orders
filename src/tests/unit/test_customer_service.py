import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.models.customers import Customer as DBCustomer
from src.app.api.schemas.customer import CustomerCreate
from src.app.api.services.customer_service import (
    get_customer_by_id,
    insert_customer,
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


@pytest.mark.asyncio
async def test_insert_customer_success(mock_db, mock_db_customer):
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
async def test_insert_customer_failure(mock_db):
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
async def test_get_customer_by_id_found(mock_db, mock_db_customer):
    customer_id = 1
    mock_result = AsyncMock()

    mock_result.scalar_one_or_none.return_value = mock_db_customer

    mock_db.execute.return_value = mock_result

    await _get_customer_by_id(mock_db, customer_id)

    mock_db.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_get_customer_by_id_failure(mock_db):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    with (
        pytest.raises(Exception),
        patch(
            "src.app.api.services.customer_service.handle_error_helper"
        ) as mock_handle_error,
    ):
        await get_customer_by_id(mock_db, 1)
        mock_handle_error.assert_called_once()


@pytest.mark.asyncio
async def test_generate_code():
    customer_id = "1"
    code = await generate_code(customer_id)
    assert code.startswith("CUST")
    assert len(code) == 21


def test_handle_error_helper():
    with patch("src.app.settings.logging.logger.error") as mock_logger:
        with pytest.raises(HTTPException) as e:
            handle_error_helper(404, "Not Found")
        assert e.value.status_code == 404
        mock_logger.assert_called_once_with("Error 404: Not Found")
