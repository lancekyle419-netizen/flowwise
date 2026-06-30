"""M-Pesa integration tests."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.mpesa import MPesaService


@pytest.fixture
def mpesa_service():
    """M-Pesa service fixture."""
    return MPesaService()


def test_format_phone_number(mpesa_service):
    """Test phone number formatting."""
    # Test with +254 prefix
    assert mpesa_service._format_phone_number("+254712345678") == "254712345678"

    # Test with 0 prefix
    assert mpesa_service._format_phone_number("0712345678") == "254712345678"

    # Test with 254 prefix
    assert mpesa_service._format_phone_number("254712345678") == "254712345678"

    # Test with spaces and dashes
    assert mpesa_service._format_phone_number("+254-712-345-678") == "254712345678"


@patch('requests.get')
def test_get_access_token(mock_get, mpesa_service):
    """Test access token generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test_token_12345"}
    mock_get.return_value = mock_response

    token = mpesa_service.get_access_token()
    assert token == "test_token_12345"
    mock_get.assert_called_once()


@patch('requests.post')
@patch('requests.get')
def test_initiate_stk_push(mock_get, mock_post, mpesa_service):
    """Test STK push initiation."""
    # Mock access token
    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "test_token"}
    mock_get.return_value = mock_token_response

    # Mock STK push response
    mock_stk_response = MagicMock()
    mock_stk_response.json.return_value = {
        "CheckoutRequestID": "ws_CO_123456",
        "ResponseCode": "0",
        "ResponseDescription": "Success",
        "MerchantRequestID": "mr_123456"
    }
    mock_post.return_value = mock_stk_response

    result = mpesa_service.initiate_stk_push(
        phone_number="0712345678",
        amount=100.0,
        account_reference="INV-001"
    )

    assert result["success"] is True
    assert result["checkout_request_id"] == "ws_CO_123456"


def test_process_callback(mpesa_service, db_session):
    """Test M-Pesa callback processing."""
    from app.models.payment import Payment
    from app.models.invoice import Invoice
    from app.models.subscription import Subscription
    from app.models.user import User
    from app.models.plan import Plan

    # Create test data
    user = User(
        phone_number="0712345678",
        first_name="Test",
        last_name="User",
        password_hash="hash"
    )
    plan = Plan(
        name="Test Plan",
        speed_mbps=10,
        price_ksh=500
    )
    db_session.add(user)
    db_session.add(plan)
    db_session.commit()

    subscription = Subscription(user_id=user.id, plan_id=plan.id)
    db_session.add(subscription)
    db_session.commit()

    invoice = Invoice(
        subscription_id=subscription.id,
        user_id=user.id,
        invoice_number="INV-001",
        amount_ksh=500,
        due_date="2026-07-30"
    )
    db_session.add(invoice)
    db_session.commit()

    payment = Payment(
        invoice_id=invoice.id,
        user_id=user.id,
        amount_ksh=500,
        mpesa_receipt_number="LIJ123456"
    )
    db_session.add(payment)
    db_session.commit()

    # Mock callback data
    callback_data = {
        "Body": {
            "stkCallback": {
                "ResultCode": 0,
                "ResultDesc": "The service request has been processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 500},
                        {"Name": "MpesaReceiptNumber", "Value": "LIJ123456"},
                        {"Name": "TransactionDate", "Value": 20260630120000},
                        {"Name": "PhoneNumber", "Value": 254712345678}
                    ]
                }
            }
        }
    }

    success = mpesa_service.process_callback(callback_data, db_session)
    assert success is True
