"""Payment model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Numeric, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class PaymentMethod(str, enum.Enum):
    """Payment method."""
    MPESA = "mpesa"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class PaymentStatus(str, enum.Enum):
    """Payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """Payment model."""

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount_ksh = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.MPESA)
    transaction_ref = Column(String(100), unique=True, index=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    mpesa_receipt_number = Column(String(50))
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.transaction_ref}>"
