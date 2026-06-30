# Flowwise Setup Guide

## Prerequisites

- Docker & Docker Compose
- Git
- Python 3.10+ (for local development without Docker)
- Node.js 18+ (for frontend development)

## Quick Start with Docker

### 1. Clone Repository

```bash
git clone https://github.com/lancekyle419-netizen/flowwise.git
cd flowwise
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Update `.env` with your configuration (M-Pesa credentials, secrets, etc.)

### 3. Start Services

```bash
docker-compose up
```

This will start:
- PostgreSQL on `localhost:5432`
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:3000`

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Database**: `localhost:5432`

## Local Development (Without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Database Setup

Database migrations are handled automatically on container startup. To manually run migrations:

```bash
cd backend
alembic upgrade head  # Apply migrations
alembic downgrade -1  # Rollback last migration
```

## Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app tests/
```

## M-Pesa Configuration

1. Register for Safaricom Daraja API at https://developer.safaricom.co.ke/
2. Get your consumer key and secret
3. Add to `.env`:
   ```
   MPESA_CONSUMER_KEY=your_key
   MPESA_CONSUMER_SECRET=your_secret
   MPESA_SHORTCODE=your_shortcode
   MPESA_PASSKEY=your_passkey
   ```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9

# Kill process on port 5432 (postgres)
lsof -ti:5432 | xargs kill -9
```

### Database Connection Issues

Ensure PostgreSQL is running and accessible:

```bash
psql postgresql://flowwise:password@localhost:5432/flowwise
```

### Docker Issues

```bash
# Clean up containers and volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up
```
