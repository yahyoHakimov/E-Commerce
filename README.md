# MARKT — E-Commerce API

Modular monolith e-commerce backend built with FastAPI, PostgreSQL, and Multicard.uz payment gateway.

## Architecture
```
app/
├── core/           Config, database, JWT security, dependencies
└── modules/
    ├── auth/       Register, login, JWT tokens
    ├── products/   CRUD with inventory management
    ├── cart/       Shopping cart per user
    └── payments/   Multicard checkout + order creation
```

Each module is self-contained: `models.py → schemas.py → service.py → router.py`

Payment gateway uses an abstract interface — swap Multicard for any provider without changing business logic.

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://localhost:8000` for the UI or `http://localhost:8000/docs` for Swagger.

## Docker
```bash
docker compose up --build
```

## Tech Stack

FastAPI · PostgreSQL · SQLAlchemy · JWT · Multicard.uz · Pydantic