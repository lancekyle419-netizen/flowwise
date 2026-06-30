"""Plan model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class PlanStatus(str, enum.Enum):
    """Plan status."""
    ACTIVE = "active"
    ARCHIVED = "archived"


class Plan(Base):
    """Internet plan model."""

    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    speed_mbps = Column(Integer)  # Speed in Mbps
    data_limit_gb = Column(Integer)  # Data limit in GB (NULL = unlimited)
    price_ksh = Column(Numeric(10, 2), nullable=False)  # Price in Kenyan Shillings
    billing_cycle_days = Column(Integer, default=30)  # 30 days monthly
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<Plan {self.name}>"
