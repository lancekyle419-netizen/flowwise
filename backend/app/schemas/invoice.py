"""Invoice schemas."""

from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.invoice import InvoiceStatus


class InvoiceCreate(BaseModel):
    """Invoice creation schema."""

    subscription_id: str
    user_id: str
    amount_ksh: Decimal = Field(..., gt=0)
    due_date: date
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response schema."""

    id: str
    subscription_id: str
    user_id: str
    invoice_number: str
    amount_ksh: Decimal
    due_date: date
    issued_date: date
    status: InvoiceStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
