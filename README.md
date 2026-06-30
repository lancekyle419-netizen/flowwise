# Flowwise - Internet Billing System for Kenyan ISP

A comprehensive billing and subscription management system designed for small Internet Service Providers (ISPs) in Kenya.

## Features

- **Customer Management**: Register and manage ISP customers
- **Plans & Subscriptions**: Define and assign internet plans with speed tiers and data limits
- **Billing & Invoicing**: Automated monthly invoice generation and tracking
- **Payment Processing**: M-Pesa integration for seamless Kenyan payments
- **Admin Dashboard**: Comprehensive business analytics and management
- **Customer Portal**: Self-service account and invoice access

## Tech Stack

- **Backend**: Python + FastAPI
- **Database**: PostgreSQL
- **Frontend**: React + TypeScript
- **Payments**: M-Pesa API (Safaricom)
- **Deployment**: Docker + Docker Compose

## Project Structure

```
flowwise/
├── backend/              # FastAPI application
├── frontend/             # React admin dashboard
├── docs/                 # Documentation
├── docker-compose.yml    # Local development setup
└── .env.example          # Environment variables template
```

## Quick Start

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

## Development

```bash
# Clone repository
git clone https://github.com/lancekyle419-netizen/flowwise.git
cd flowwise

# Start services with Docker Compose
docker-compose up

# Backend runs on: http://localhost:8000
# Frontend runs on: http://localhost:3000
# PostgreSQL runs on: localhost:5432
```

## License

MIT License - See LICENSE file for details
