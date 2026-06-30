"""Billing service for invoice and subscription management."""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod


class BillingService:
    """Billing service."""

    @staticmethod
    def create_subscription(
        user_id: str, plan_id: str, db: Session
    ) -> Optional[Subscription]:
        """Create a new subscription."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            plan = db.query(Plan).filter(Plan.id == plan_id).first()

            if not user or not plan:
                return None

            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                start_date=date.today(),
                status=SubscriptionStatus.ACTIVE,
            )

            db.add(subscription)
            db.commit()
            db.refresh(subscription)

            # Create first invoice
            BillingService.create_invoice_for_subscription(subscription, db)

            return subscription
        except Exception as e:
            print(f"Error creating subscription: {e}")
            db.rollback()
            return None

    @staticmethod
    def create_invoice_for_subscription(
        subscription: Subscription, db: Session
    ) -> Optional[Invoice]:
        """Create an invoice for a subscription."""
        try:
            plan = subscription.plan
            user = subscription.user

            # Generate invoice number
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            # Set due date (30 days from today)
            due_date = date.today() + timedelta(days=30)

            invoice = Invoice(
                subscription_id=subscription.id,
                user_id=user.id,
                invoice_number=invoice_number,
                amount_ksh=plan.price_ksh,
                due_date=due_date,
                status=InvoiceStatus.SENT,
            )

            db.add(invoice)
            db.commit()
            db.refresh(invoice)

            return invoice
        except Exception as e:
            print(f"Error creating invoice: {e}")
            db.rollback()
            return None

    @staticmethod
    def generate_monthly_invoices(db: Session) -> List[Invoice]:
        """Generate monthly invoices for active subscriptions."""
        created_invoices = []
        try:
            # Get all active subscriptions
            subscriptions = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).all()

            for subscription in subscriptions:
                # Check if invoice already exists for this month
                today = date.today()
                existing_invoice = db.query(Invoice).filter(
                    Invoice.subscription_id == subscription.id,
                    Invoice.issued_date >= date(today.year, today.month, 1),
                ).first()

                if not existing_invoice:
                    invoice = BillingService.create_invoice_for_subscription(
                        subscription, db
                    )
                    if invoice:
                        created_invoices.append(invoice)

            return created_invoices
        except Exception as e:
            print(f"Error generating monthly invoices: {e}")
            return created_invoices

    @staticmethod
    def mark_invoice_as_overdue(db: Session) -> int:
        """Mark invoices as overdue if due date has passed."""
        try:
            invoices = db.query(Invoice).filter(
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date < date.today(),
            ).all()

            for invoice in invoices:
                invoice.status = InvoiceStatus.OVERDUE
                invoice.updated_at = datetime.utcnow()

            db.commit()
            return len(invoices)
        except Exception as e:
            print(f"Error marking invoices as overdue: {e}")
            db.rollback()
            return 0

    @staticmethod
    def get_customer_invoices(
        user_id: str, db: Session, limit: int = 100
    ) -> List[Invoice]:
        """Get invoices for a customer."""
        try:
            invoices = db.query(Invoice).filter(
                Invoice.user_id == user_id
            ).order_by(Invoice.created_at.desc()).limit(limit).all()
            return invoices
        except Exception as e:
            print(f"Error fetching customer invoices: {e}")
            return []

    @staticmethod
    def get_customer_subscription(
        user_id: str, db: Session
    ) -> Optional[Subscription]:
        """Get active subscription for a customer."""
        try:
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            ).first()
            return subscription
        except Exception as e:
            print(f"Error fetching customer subscription: {e}")
            return None

    @staticmethod
    def cancel_subscription(
        subscription_id: str, db: Session
    ) -> Optional[Subscription]:
        """Cancel a subscription."""
        try:
            subscription = db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()

            if subscription:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.end_date = date.today()
                subscription.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(subscription)

            return subscription
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
            db.rollback()
            return None
