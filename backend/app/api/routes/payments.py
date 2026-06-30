"""Payment routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    """Create a payment."""
    # Validate invoice exists
    from app.models.invoice import Invoice
    invoice = db.query(Invoice).filter(Invoice.id == payment_data.invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    new_payment = Payment(**payment_data.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@router.get("/", response_model=List[PaymentResponse])
def list_payments(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """List payments."""
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str, db: Session = Depends(get_db)):
    """Get payment details."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


@router.post("/mpesa/callback")
def mpesa_callback(data: dict):
    """M-Pesa payment callback endpoint."""
    # This will be implemented with the M-Pesa integration service
    return {"status": "success"}
