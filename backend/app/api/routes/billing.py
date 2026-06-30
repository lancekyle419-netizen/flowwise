"""Billing routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse

router = APIRouter()


@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """List invoices."""
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    """Get invoice details."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice
