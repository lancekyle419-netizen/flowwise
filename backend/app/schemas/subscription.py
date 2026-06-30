"""Subscription schemas."""

from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.subscription import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    """Subscription creation schema."""

    user_id: str
    plan_id: str
    auto_renew: bool = Field(default=True)


class SubscriptionResponse(BaseModel):
    """Subscription response schema."""

    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    start_date: date
    end_date: date | None
    auto_renew: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
