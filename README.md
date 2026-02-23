# MARKT — E-Commerce API

Modular monolith e-commerce backend built with FastAPI, PostgreSQL, and Stripe.

## Architecture

```
app/
├── core/           Config, database, JWT security, dependencies
└── modules/
    ├── auth/       Register, login, JWT tokens
    ├── products/   CRUD with inventory management
    ├── cart/       Shopping cart per user
    └── payments/   Stripe checkout + order creation
```

Each module is self-contained: `models.py → schemas.py → service.py → router.py`

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # edit with your credentials

# Run
uvicorn app.main:app --reload
```

Open `http://localhost:8000` for the UI or `http://localhost:8000/docs` for Swagger.

## Docker

```bash
docker compose up --build
```

## Tech Stack

FastAPI · PostgreSQL · SQLAlchemy · JWT · Stripe · Pydantic