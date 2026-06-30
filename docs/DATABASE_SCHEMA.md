# Flowwise Database Schema

## Overview

This document outlines the core database tables for the billing system.

## Tables

### Users (Customers)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    location VARCHAR(255),
    status ENUM('active', 'suspended', 'inactive'),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Plans

```sql
CREATE TABLE plans (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    speed_mbps INTEGER,
    data_limit_gb INTEGER,
    price_ksh DECIMAL(10, 2),
    billing_cycle_days INTEGER,
    status ENUM('active', 'archived'),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Subscriptions

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    plan_id UUID REFERENCES plans(id),
    status ENUM('active', 'suspended', 'cancelled'),
    start_date DATE,
    end_date DATE,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Invoices

```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    subscription_id UUID REFERENCES subscriptions(id),
    user_id UUID REFERENCES users(id),
    invoice_number VARCHAR(50) UNIQUE,
    amount_ksh DECIMAL(10, 2),
    due_date DATE,
    issued_date DATE,
    status ENUM('draft', 'sent', 'paid', 'overdue', 'cancelled'),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Payments

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    invoice_id UUID REFERENCES invoices(id),
    user_id UUID REFERENCES users(id),
    amount_ksh DECIMAL(10, 2),
    payment_method ENUM('mpesa', 'cash', 'bank_transfer', 'other'),
    transaction_ref VARCHAR(100),
    status ENUM('pending', 'completed', 'failed', 'refunded'),
    mpesa_receipt_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Usage Tracking (Optional)

```sql
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY,
    subscription_id UUID REFERENCES subscriptions(id),
    data_used_gb DECIMAL(10, 2),
    logged_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```
