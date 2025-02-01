import datetime
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from src.app.api.services.customer_service import (
    insert_customer,
    get_customer_by_id,
    get_all_customers,
    update_customer_by_id,
    delete_customer_by_id,
)
from src.app.api.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    Customer,
)
from src.app.api.models.customers import Customer as DBCustomer
from src.app.api.utils.error_handler import handle_error_helper
from src.app.api.utils.code_generator import generate_cust_code
from src.app.api.utils.customer_utils import update_customer_helper


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_db_customer():
    return MagicMock(
        spec=DBCustomer, name="Test Name", phone_number="1234567890", id=1
    )


@pytest.fixture
def mock_customer_create():
    mock = MagicMock(spec=CustomerCreate)
    mock.name = "Test Name"
    mock.phone_number = "1234567890"
    mock.id = "CUST001"
    mock.code = "CODE001"
    return mock


@pytest.fixture
def mock_customer_update():
    mock = MagicMock(spec=CustomerUpdate)
    mock.name = "Updated Name"
    mock.phone_number = "9876543210"
    mock.code = "CODE002"
    return mock


def test_insert_customer_success(mock_db, mock_customer_create):
    with (
        patch(
            "src.app.api.utils.error_handler.handle_error_helper"
        ) as mock_handle_error,
    ):

        insert_customer(mock_db, mock_customer_create)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert mock_customer_create.code == "CODE001"
        mock_handle_error.assert_not_called()


def test_insert_customer_failure(mock_db, mock_customer_create):
    mock_db.add.side_effect = SQLAlchemyError()

    with pytest.raises(HTTPException) as e:
        insert_customer(mock_db, mock_customer_create)

    assert e.value.status_code == 500


def test_get_customer_by_id_success(mock_db, mock_db_customer):
    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_db_customer
    )

    result = get_customer_by_id(mock_db, 1)
    assert isinstance(result, DBCustomer)
    mock_db.query.assert_called_once()
    assert result.id == 1


def test_get_customer_by_id_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as e:
        get_customer_by_id(mock_db, 1)
    assert e.value.status_code == 404


def test_get_customer_by_id_failure(mock_db):
    mock_db.query.return_value.filter.return_value.first.side_effect = (
        SQLAlchemyError()
    )
    with pytest.raises(HTTPException) as e:
        get_customer_by_id(mock_db, 1)
    assert e.value.status_code == 500


def test_get_all_customers_success(mock_db, mock_db_customer):
    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = [  # noqa
        mock_db_customer
    ]
    with patch(
        "src.app.api.schemas.customer.Customer.model_validate"
    ) as mock_validate:
        mock_validate.return_value = Customer(
            id=1,
            name="Test Name",
            phone_number="1234567890",
            code="CODE001",
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        result = get_all_customers(mock_db, skip=0, limit=1)
        assert isinstance(result[0], Customer)


def test_get_all_customers_failure(mock_db):
    mock_db.query.return_value.offset.return_value.limit.return_value.all.side_effect = (  # noqa
        SQLAlchemyError()
    )
    with pytest.raises(HTTPException) as e:
        get_all_customers(mock_db, skip=0, limit=1)
    assert e.value.status_code == 500


def test_update_customer_by_id_success(
    mock_db, mock_db_customer, mock_customer_update
):
    with (
        patch(
            "src.app.api.services.customer_service.get_customer_by_id"
        ) as mock_get,
        patch(
            "src.app.api.services.customer_service.Customer.model_validate"
        ) as mock_model_validate,
    ):
        mock_get.return_value = mock_db_customer
        mock_model_validate.return_value = mock_db_customer

        result = update_customer_by_id(mock_db, 1, mock_customer_update)

        mock_get.assert_called_once_with(mock_db, 1)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_db_customer)
        mock_model_validate.assert_called_once_with(mock_db_customer)
        assert result == mock_db_customer


def test_update_customer_by_id_failure(
    mock_db, mock_db_customer, mock_customer_update
):
    with (
        patch(
            "src.app.api.services.customer_service.get_customer_by_id"
        ) as mock_get,
    ):
        mock_get.return_value = mock_db_customer
        mock_db.commit.side_effect = SQLAlchemyError()

        with pytest.raises(HTTPException) as e:
            update_customer_by_id(mock_db, 1, mock_customer_update)
        assert e.value.status_code == 500
        mock_db.rollback.assert_called_once()


def test_delete_customer_by_id_success(mock_db, mock_db_customer):
    with patch(
        "src.app.api.services.customer_service.get_customer_by_id"
    ) as mock_get:
        mock_get.return_value = mock_db_customer
        delete_customer_by_id(mock_db, 1)
        mock_get.assert_called_once_with(mock_db, 1)
        mock_db.delete.assert_called_once_with(mock_db_customer)
        mock_db.commit.assert_called_once()


def test_delete_customer_by_id_failure(mock_db, mock_db_customer):
    with patch(
        "src.app.api.services.customer_service.get_customer_by_id"
    ) as mock_get:
        mock_get.return_value = mock_db_customer
        mock_db.commit.side_effect = SQLAlchemyError()
        with pytest.raises(HTTPException) as e:
            delete_customer_by_id(mock_db, 1)
        assert e.value.status_code == 500
        mock_db.rollback.assert_called_once()
        mock_get.assert_called_once_with(mock_db, 1)
        mock_db.delete.assert_called_once_with(mock_db_customer)


def test_handle_error_helper():
    with patch("src.app.settings.logging.logger.error") as mock_logger:
        with pytest.raises(HTTPException) as e:
            handle_error_helper(404, "Not Found")
        assert e.value.status_code == 404
        mock_logger.assert_called_once_with("Not Found")


def test_update_customer_helper_success(
    mock_db_customer, mock_customer_update
):
    update_customer_helper(mock_db_customer, mock_customer_update)
    mock_db_customer.name = mock_customer_update.name
    mock_db_customer.phone_number = mock_customer_update.phone_number


def test_update_customer_helper_failure(
    mock_db_customer, mock_customer_update
):
    mock_customer_update.__iter__.side_effect = Exception("Mocked exception")

    with pytest.raises(HTTPException) as e:
        update_customer_helper(mock_db_customer, mock_customer_update)
    assert e.value.status_code == 400


def test_generate_cust_code():
    customer_id = "1"
    code = generate_cust_code(customer_id)
    assert code.startswith("CUST")
    assert len(code) == 21
