"""User schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserStatus


class UserCreate(BaseModel):
    """User creation schema."""

    phone_number: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema."""

    phone_number: str
    password: str


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    phone_number: str
    email: Optional[str]
    first_name: str
    last_name: str
    location: Optional[str]
    status: UserStatus
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
