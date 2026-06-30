"""Plan schemas."""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.plan import PlanStatus


class PlanCreate(BaseModel):
    """Plan creation schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    speed_mbps: int = Field(..., gt=0)
    data_limit_gb: Optional[int] = Field(None, gt=0)
    price_ksh: Decimal = Field(..., gt=0)
    billing_cycle_days: int = Field(default=30, gt=0)


class PlanResponse(BaseModel):
    """Plan response schema."""

    id: str
    name: str
    description: Optional[str]
    speed_mbps: int
    data_limit_gb: Optional[int]
    price_ksh: Decimal
    billing_cycle_days: int
    status: PlanStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
