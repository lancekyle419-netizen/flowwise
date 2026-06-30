"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, customers, plans, billing, payments
from app.config import settings
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Flowwise API",
    description="Internet Billing System for Kenyan ISP",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["plans"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Flowwise API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
