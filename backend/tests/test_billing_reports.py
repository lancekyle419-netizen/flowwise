"""Billing report tests."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.reports.billing_report import BillingReport


@pytest.fixture
def setup_billing_data(db_session):
    """Set up test billing data."""
    # Create users
    user1 = User(
        phone_number="0712345678",
        first_name="Test",
        last_name="User1",
        password_hash="hash"
    )
    user2 = User(
        phone_number="0722345678",
        first_name="Test",
        last_name="User2",
        password_hash="hash"
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    # Create plan
    plan = Plan(
        name="Test Plan",
        speed_mbps=10,
        price_ksh=Decimal(500)
    )
    db_session.add(plan)
    db_session.commit()

    # Create subscriptions
    sub1 = Subscription(user_id=user1.id, plan_id=plan.id)
    sub2 = Subscription(user_id=user2.id, plan_id=plan.id)
    db_session.add(sub1)
    db_session.add(sub2)
    db_session.commit()

    # Create invoices
    inv1 = Invoice(
        subscription_id=sub1.id,
        user_id=user1.id,
        invoice_number="INV-001",
        amount_ksh=Decimal(500),
        due_date=date.today() + timedelta(days=30),
        status=InvoiceStatus.SENT
    )
    inv2 = Invoice(
        subscription_id=sub2.id,
        user_id=user2.id,
        invoice_number="INV-002",
        amount_ksh=Decimal(1000),
        due_date=date.today() - timedelta(days=5),
        status=InvoiceStatus.OVERDUE
    )
    db_session.add(inv1)
    db_session.add(inv2)
    db_session.commit()

    # Create payments
    pay1 = Payment(
        invoice_id=inv1.id,
        user_id=user1.id,
        amount_ksh=Decimal(500),
        payment_method=PaymentMethod.MPESA,
        status=PaymentStatus.COMPLETED,
        transaction_ref="TXN-001"
    )
    pay2 = Payment(
        invoice_id=inv2.id,
        user_id=user2.id,
        amount_ksh=Decimal(1000),
        payment_method=PaymentMethod.MPESA,
        status=PaymentStatus.PENDING,
        transaction_ref="TXN-002"
    )
    db_session.add(pay1)
    db_session.add(pay2)
    db_session.commit()

    return {
        "users": [user1, user2],
        "plan": plan,
        "subscriptions": [sub1, sub2],
        "invoices": [inv1, inv2],
        "payments": [pay1, pay2]
    }


def test_revenue_summary(setup_billing_data, db_session):
    """Test revenue summary report."""
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()

    report = BillingReport.get_revenue_summary(db_session, start_date, end_date)

    assert "total_revenue_ksh" in report
    assert "payment_count" in report
    assert report["payment_count"] == 1  # Only one completed payment


def test_customer_summary(setup_billing_data, db_session):
    """Test customer summary report."""
    report = BillingReport.get_customer_summary(db_session)

    assert "total_customers" in report
    assert "active_subscriptions" in report
    assert report["total_customers"] >= 2
    assert report["active_subscriptions"] >= 2


def test_invoice_summary(setup_billing_data, db_session):
    """Test invoice summary report."""
    report = BillingReport.get_invoice_summary(db_session)

    assert "count" in report
    assert "total_amount_ksh" in report
    assert report["count"] >= 2


def test_overdue_report(setup_billing_data, db_session):
    """Test overdue payment report."""
    report = BillingReport.get_overdue_report(db_session)

    assert "total_overdue_ksh" in report
    assert "invoice_count" in report
    assert report["total_overdue_ksh"] > 0
    assert report["invoice_count"] >= 1


def test_payment_method_summary(setup_billing_data, db_session):
    """Test payment method summary report."""
    report = BillingReport.get_payment_method_summary(db_session)

    assert "mpesa" in report
    assert report["mpesa"]["count"] >= 1


def test_monthly_comparison(setup_billing_data, db_session):
    """Test monthly comparison report."""
    report = BillingReport.get_monthly_comparison(db_session, months=3)

    assert len(report) == 3
    for entry in report:
        assert "month" in entry
        assert "revenue_ksh" in entry
        assert "payment_count" in entry
