"""Enhanced billing routes with reporting and analytics."""

from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.invoice import InvoiceStatus
from app.reports.billing_report import BillingReport

router = APIRouter()


@router.get("/reports/revenue-summary")
def get_revenue_summary(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Get revenue summary for a date range."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    report = BillingReport.get_revenue_summary(db, start_date, end_date)
    return report


@router.get("/reports/customer-summary")
def get_customer_summary(db: Session = Depends(get_db)):
    """Get customer summary."""
    report = BillingReport.get_customer_summary(db)
    return report


@router.get("/reports/invoice-summary")
def get_invoice_summary(status: str = None, db: Session = Depends(get_db)):
    """Get invoice summary."""
    invoice_status = None
    if status:
        try:
            invoice_status = InvoiceStatus[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    report = BillingReport.get_invoice_summary(db, invoice_status)
    return report


@router.get("/reports/overdue")
def get_overdue_report(db: Session = Depends(get_db)):
    """Get overdue payment report."""
    report = BillingReport.get_overdue_report(db)
    return report


@router.get("/reports/payment-methods")
def get_payment_method_summary(db: Session = Depends(get_db)):
    """Get payment method breakdown."""
    report = BillingReport.get_payment_method_summary(db)
    return report


@router.get("/reports/monthly-comparison")
def get_monthly_comparison(months: int = 3, db: Session = Depends(get_db)):
    """Get monthly revenue comparison."""
    if months < 1 or months > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Months must be between 1 and 12"
        )

    report = BillingReport.get_monthly_comparison(db, months)
    return report


@router.post("/admin/generate-invoices")
def admin_generate_invoices(db: Session = Depends(get_db)):
    """Admin endpoint to manually generate invoices."""
    from app.services.billing import BillingService
    
    invoices = BillingService.generate_monthly_invoices(db)
    return {
        "success": True,
        "invoices_generated": len(invoices),
        "message": f"Generated {len(invoices)} invoices"
    }


@router.post("/admin/mark-overdue")
def admin_mark_overdue(db: Session = Depends(get_db)):
    """Admin endpoint to manually mark invoices as overdue."""
    from app.services.billing import BillingService
    
    count = BillingService.mark_invoice_as_overdue(db)
    return {
        "success": True,
        "invoices_marked": count,
        "message": f"Marked {count} invoices as overdue"
    }


@router.post("/admin/auto-renew-subscriptions")
def admin_auto_renew_subscriptions(db: Session = Depends(get_db)):
    """Admin endpoint to manually trigger auto-renewal."""
    from app.tasks.scheduler import BillingScheduler
    
    count = BillingScheduler.auto_renew_subscriptions()
    return {
        "success": True,
        "subscriptions_renewed": count,
        "message": f"Auto-renewed {count} subscriptions"
    }
