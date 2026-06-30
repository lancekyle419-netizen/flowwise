"""Billing report generation."""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus
from app.models.subscription import Subscription, SubscriptionStatus


class BillingReport:
    """Billing report generator."""

    @staticmethod
    def get_revenue_summary(db: Session, start_date: date, end_date: date) -> Dict:
        """Get revenue summary for a date range."""
        payments = db.query(Payment).filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at >= start_date,
            Payment.created_at <= end_date
        ).all()

        total_revenue = sum(payment.amount_ksh for payment in payments)
        payment_count = len(payments)
        average_payment = total_revenue / payment_count if payment_count > 0 else Decimal(0)

        return {
            "period": f"{start_date} to {end_date}",
            "total_revenue_ksh": float(total_revenue),
            "payment_count": payment_count,
            "average_payment_ksh": float(average_payment),
        }

    @staticmethod
    def get_customer_summary(db: Session) -> Dict:
        """Get customer summary."""
        total_customers = db.query(func.count(User.id)).scalar() or 0
        active_subscriptions = db.query(func.count(Subscription.id)).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).scalar() or 0
        suspended_subscriptions = db.query(func.count(Subscription.id)).filter(
            Subscription.status == SubscriptionStatus.SUSPENDED
        ).scalar() or 0
        cancelled_subscriptions = db.query(func.count(Subscription.id)).filter(
            Subscription.status == SubscriptionStatus.CANCELLED
        ).scalar() or 0

        return {
            "total_customers": total_customers,
            "active_subscriptions": active_subscriptions,
            "suspended_subscriptions": suspended_subscriptions,
            "cancelled_subscriptions": cancelled_subscriptions,
        }

    @staticmethod
    def get_invoice_summary(db: Session, status: Optional[InvoiceStatus] = None) -> Dict:
        """Get invoice summary."""
        query = db.query(Invoice)
        if status:
            query = query.filter(Invoice.status == status)

        invoices = query.all()
        total_amount = sum(invoice.amount_ksh for invoice in invoices)
        invoice_count = len(invoices)
        average_amount = total_amount / invoice_count if invoice_count > 0 else Decimal(0)

        return {
            "status": status.value if status else "all",
            "count": invoice_count,
            "total_amount_ksh": float(total_amount),
            "average_amount_ksh": float(average_amount),
        }

    @staticmethod
    def get_overdue_report(db: Session) -> Dict:
        """Get overdue payment report."""
        today = date.today()
        overdue_invoices = db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.OVERDUE,
            Invoice.due_date < today
        ).all()

        total_overdue = sum(invoice.amount_ksh for invoice in overdue_invoices)
        
        # Group by customer
        customer_overdue = {}
        for invoice in overdue_invoices:
            user_id = str(invoice.user_id)
            if user_id not in customer_overdue:
                customer_overdue[user_id] = {
                    "customer": invoice.user,
                    "amount_ksh": Decimal(0),
                    "invoice_count": 0,
                }
            customer_overdue[user_id]["amount_ksh"] += invoice.amount_ksh
            customer_overdue[user_id]["invoice_count"] += 1

        return {
            "total_overdue_ksh": float(total_overdue),
            "invoice_count": len(overdue_invoices),
            "customers_with_overdue": {
                user_id: {
                    "customer_phone": data["customer"].phone_number,
                    "amount_ksh": float(data["amount_ksh"]),
                    "invoice_count": data["invoice_count"],
                }
                for user_id, data in customer_overdue.items()
            },
        }

    @staticmethod
    def get_payment_method_summary(db: Session) -> Dict:
        """Get payment method breakdown."""
        from app.models.payment import PaymentMethod
        
        payments = db.query(Payment).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).all()

        method_summary = {}
        for method in PaymentMethod:
            method_payments = [p for p in payments if p.payment_method == method]
            total = sum(p.amount_ksh for p in method_payments)
            method_summary[method.value] = {
                "count": len(method_payments),
                "total_ksh": float(total),
            }

        return method_summary

    @staticmethod
    def get_monthly_comparison(db: Session, months: int = 3) -> List[Dict]:
        """Get monthly revenue comparison."""
        today = date.today()
        months_data = []

        for i in range(months):
            month_start = date(today.year, today.month, 1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)

            payments = db.query(Payment).filter(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.created_at >= month_start,
                Payment.created_at <= month_end
            ).all()

            total_revenue = sum(p.amount_ksh for p in payments)
            months_data.append({
                "month": month_start.strftime("%B %Y"),
                "revenue_ksh": float(total_revenue),
                "payment_count": len(payments),
            })

        return months_data
