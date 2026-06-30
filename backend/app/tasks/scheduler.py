"""Scheduled tasks and background jobs."""

import asyncio
from datetime import datetime, date, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import User
from app.services.billing import BillingService


class BillingScheduler:
    """Billing scheduler for recurring tasks."""

    @staticmethod
    def generate_monthly_invoices():
        """Generate invoices for all active subscriptions."""
        db = SessionLocal()
        try:
            invoices = BillingService.generate_monthly_invoices(db)
            print(f"Generated {len(invoices)} invoices")
            return len(invoices)
        finally:
            db.close()

    @staticmethod
    def mark_overdue_invoices():
        """Mark invoices as overdue."""
        db = SessionLocal()
        try:
            count = BillingService.mark_invoice_as_overdue(db)
            print(f"Marked {count} invoices as overdue")
            return count
        finally:
            db.close()

    @staticmethod
    def auto_renew_subscriptions():
        """Auto-renew subscriptions that are due."""
        db = SessionLocal()
        try:
            today = date.today()
            
            # Find subscriptions that need renewal
            subscriptions = db.query(Subscription).filter(
                Subscription.auto_renew == True,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.end_date <= today
            ).all()

            renewed_count = 0
            for subscription in subscriptions:
                # Extend subscription
                plan = subscription.plan
                subscription.end_date = today + timedelta(days=plan.billing_cycle_days)
                subscription.updated_at = datetime.utcnow()
                
                # Create new invoice
                BillingService.create_invoice_for_subscription(subscription, db)
                renewed_count += 1

            db.commit()
            print(f"Auto-renewed {renewed_count} subscriptions")
            return renewed_count
        except Exception as e:
            print(f"Error in auto-renew: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

    @staticmethod
    def send_payment_reminders():
        """Send payment reminders for upcoming due dates."""
        db = SessionLocal()
        try:
            today = date.today()
            reminder_date = today + timedelta(days=3)  # Remind 3 days before due
            
            invoices = db.query(Invoice).filter(
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date == reminder_date
            ).all()

            # TODO: Integrate with SMS service to send reminders
            print(f"Found {len(invoices)} invoices to send reminders for")
            return len(invoices)
        finally:
            db.close()

    @staticmethod
    def suspend_overdue_subscriptions():
        """Suspend subscriptions with overdue invoices."""
        db = SessionLocal()
        try:
            # Get invoices overdue by more than 30 days
            cutoff_date = date.today() - timedelta(days=30)
            
            overdue_invoices = db.query(Invoice).filter(
                Invoice.status == InvoiceStatus.OVERDUE,
                Invoice.due_date <= cutoff_date
            ).all()

            suspended_count = 0
            for invoice in overdue_invoices:
                subscription = invoice.subscription
                if subscription.status == SubscriptionStatus.ACTIVE:
                    subscription.status = SubscriptionStatus.SUSPENDED
                    subscription.updated_at = datetime.utcnow()
                    suspended_count += 1

            db.commit()
            print(f"Suspended {suspended_count} subscriptions")
            return suspended_count
        except Exception as e:
            print(f"Error suspending subscriptions: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

    @staticmethod
    def generate_usage_report():
        """Generate daily usage report."""
        db = SessionLocal()
        try:
            from app.models.usage import UsageLog
            
            today = date.today()
            usage_logs = db.query(UsageLog).filter(
                UsageLog.logged_date == today
            ).all()

            total_data = sum(log.data_used_gb for log in usage_logs)
            print(f"Daily data usage: {total_data} GB")
            return {"date": today, "total_data_gb": total_data}
        finally:
            db.close()
