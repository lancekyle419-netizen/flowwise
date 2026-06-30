"""Customer management routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def list_customers(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """List all customers."""
    customers = db.query(User).offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=UserResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get customer details."""
    customer = db.query(User).filter(User.id == customer_id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer
