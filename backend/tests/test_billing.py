"""Billing service tests."""

import pytest
from datetime import date, timedelta
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.services.billing import BillingService


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        phone_number="0712345678",
        first_name="Test",
        last_name="User",
        password_hash="hash"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_plan(db_session):
    """Create a test plan."""
    plan = Plan(
        name="Test Plan",
        speed_mbps=10,
        price_ksh=500
    )
    db_session.add(plan)
    db_session.commit()
    return plan


def test_create_subscription(test_user, test_plan, db_session):
    """Test subscription creation."""
    subscription = BillingService.create_subscription(
        str(test_user.id), str(test_plan.id), db_session
    )

    assert subscription is not None
    assert subscription.user_id == test_user.id
    assert subscription.plan_id == test_plan.id
    assert subscription.status == SubscriptionStatus.ACTIVE


def test_create_invoice_for_subscription(test_user, test_plan, db_session):
    """Test invoice creation for subscription."""
    subscription = BillingService.create_subscription(
        str(test_user.id), str(test_plan.id), db_session
    )
    
    # Invoice should be created automatically
    invoice = db_session.query(Invoice).filter(
        Invoice.subscription_id == subscription.id
    ).first()

    assert invoice is not None
    assert invoice.status == InvoiceStatus.SENT
    assert invoice.amount_ksh == test_plan.price_ksh


def test_get_customer_invoices(test_user, test_plan, db_session):
    """Test fetching customer invoices."""
    subscription = BillingService.create_subscription(
        str(test_user.id), str(test_plan.id), db_session
    )

    invoices = BillingService.get_customer_invoices(str(test_user.id), db_session)

    assert len(invoices) > 0
    assert invoices[0].user_id == test_user.id


def test_cancel_subscription(test_user, test_plan, db_session):
    """Test subscription cancellation."""
    subscription = BillingService.create_subscription(
        str(test_user.id), str(test_plan.id), db_session
    )

    cancelled = BillingService.cancel_subscription(str(subscription.id), db_session)

    assert cancelled is not None
    assert cancelled.status == SubscriptionStatus.CANCELLED
    assert cancelled.end_date == date.today()
