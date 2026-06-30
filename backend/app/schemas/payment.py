"""Payment schemas."""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    """Payment creation schema."""

    invoice_id: str
    user_id: str
    amount_ksh: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.MPESA
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema."""

    id: str
    invoice_id: str
    user_id: str
    amount_ksh: Decimal
    payment_method: PaymentMethod
    transaction_ref: Optional[str]
    status: PaymentStatus
    mpesa_receipt_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
