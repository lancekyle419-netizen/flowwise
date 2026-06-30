"""Enhanced payment routes with M-Pesa integration."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.invoice import Invoice
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.mpesa import MPesaService
from app.services.billing import BillingService

router = APIRouter()
mpesa_service = MPesaService()


@router.post("/initiate-stk-push")
def initiate_stk_push(
    phone_number: str,
    amount: float,
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """Initiate M-Pesa STK push for payment."""
    # Validate invoice
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Initiate STK push
    result = mpesa_service.initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        account_reference=f"INV-{invoice.invoice_number}",
        transaction_desc=f"Payment for {invoice.invoice_number}"
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to initiate payment")
        )

    # Create pending payment record
    payment = Payment(
        invoice_id=invoice_id,
        user_id=invoice.user_id,
        amount_ksh=amount,
        payment_method="mpesa",
        transaction_ref=result.get("checkout_request_id"),
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "success": True,
        "message": "STK push initiated",
        "checkout_request_id": result.get("checkout_request_id"),
        "payment_id": str(payment.id)
    }


@router.get("/check-payment-status/{payment_id}", response_model=PaymentResponse)
def check_payment_status(payment_id: str, db: Session = Depends(get_db)):
    """Check the status of a payment."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


@router.post("/mpesa/callback")
def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    """M-Pesa payment callback endpoint."""
    try:
        # In production, verify the callback signature
        callback_data = request.json() if hasattr(request, 'json') else {}
        
        success = mpesa_service.process_callback(callback_data, db)
        
        return {
            "ResultCode": 0,
            "ResultDesc": "Received successfully" if success else "Processed with errors"
        }
    except Exception as e:
        print(f"Callback error: {e}")
        return {
            "ResultCode": 1,
            "ResultDesc": "Error processing callback"
        }


@router.post("/create-subscription")
def create_subscription(
    user_id: str,
    plan_id: str,
    db: Session = Depends(get_db)
):
    """Create a subscription for a customer."""
    subscription = BillingService.create_subscription(user_id, plan_id, db)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create subscription"
        )

    return {
        "success": True,
        "subscription_id": str(subscription.id),
        "message": "Subscription created successfully"
    }


@router.get("/customer-invoices/{user_id}")
def get_customer_invoices(user_id: str, db: Session = Depends(get_db)):
    """Get all invoices for a customer."""
    invoices = BillingService.get_customer_invoices(user_id, db)
    return {
        "user_id": user_id,
        "invoices": invoices,
        "count": len(invoices)
    }


@router.get("/customer-subscription/{user_id}")
def get_customer_subscription(user_id: str, db: Session = Depends(get_db)):
    """Get active subscription for a customer."""
    subscription = BillingService.get_customer_subscription(user_id, db)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    return subscription


@router.post("/cancel-subscription/{subscription_id}")
def cancel_subscription(subscription_id: str, db: Session = Depends(get_db)):
    """Cancel a subscription."""
    subscription = BillingService.cancel_subscription(subscription_id, db)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    return {
        "success": True,
        "subscription_id": str(subscription.id),
        "message": "Subscription cancelled successfully"
    }
