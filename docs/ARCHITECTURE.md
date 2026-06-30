# Flowwise Architecture

## System Overview

Flowwise is a three-tier billing system for Kenyan ISPs:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│              Admin Dashboard + Customer Portal              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    API Layer (FastAPI)                      │
│  ┌──────────────┬──────────────┬─────────────┬────────────┐ │
│  │  Auth        │  Customers   │  Billing    │  Payments  │ │
│  │  Endpoints   │  Endpoints   │  Endpoints  │ Endpoints  │ │
│  └──────────────┴──────────────┴─────────────┴────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Business Logic Layer                          │
│  ┌──────────────┬──────────────┬─────────────┬────────────┐ │
│  │  Customer    │  Billing     │  Invoice    │  Payment   │ │
│  │  Service     │  Service     │  Service    │  Service   │ │
│  └──────────────┴──────────────┴─────────────┴────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Data Access Layer                             │
│  ┌──────────────┬──────────────┬─────────────┬────────────┐ │
│  │  User        │  Plan        │  Invoice    │  Payment   │ │
│  │  Repository  │  Repository  │  Repository │ Repository │ │
│  └──────────────┴──────────────┴─────────────┴────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                   PostgreSQL Database                       │
└─────────────────────────────────────────────────────────────┘

                      External Services
┌─────────────────────────────────────────────────────────────┐
│  M-Pesa (Safaricom Daraja API) - Payment Processing         │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Authentication & Authorization
- JWT token-based auth
- Role-based access control (Admin, Customer)
- Secure password handling

### 2. Customer Management
- User registration and profile management
- Contact information storage
- Account status tracking

### 3. Plans & Subscriptions
- Plan creation and management
- Subscription assignment to customers
- Auto-renewal configuration

### 4. Billing Engine
- Automatic invoice generation
- Invoice numbering and tracking
- Due date calculation
- Payment status management

### 5. Payment Processing
- M-Pesa STK push integration
- Payment reconciliation
- Receipt generation
- Partial payment handling

### 6. Dashboard & Reporting
- Customer metrics
- Revenue analytics
- Outstanding payment reports
- Usage statistics

## Data Flow

### Customer Signup Flow
1. Customer registers via API → 2. Stored in database → 3. Customer assigned to plan

### Billing Flow
1. Scheduled job triggers monthly → 2. Invoice generated → 3. Invoice sent to customer
4. Customer receives notification → 5. Payment initiated via M-Pesa

### Payment Flow
1. Customer initiates payment → 2. STK push sent to phone → 3. Customer enters PIN
4. M-Pesa API confirms payment → 5. Payment recorded → 6. Invoice marked paid
7. Receipt generated and sent

## Deployment Architecture

```
Development: Docker Compose (all services locally)
Staging: Kubernetes (cloud-based staging)
Production: AWS/DigitalOcean with RDS PostgreSQL
```
