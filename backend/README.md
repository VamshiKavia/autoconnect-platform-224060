# FastAPI Backend - Ocean Motors (Mock)

Mock backend with CORS for the React SPA. Implements in-memory endpoints (no database).

## Routes

- Health
  - GET / -> health with metadata
  - GET /docs/guide -> docs helper
  - GET /api/docs/websocket -> websocket usage note
- Auth (mirror without and with /api prefix)
  - POST /auth/register
  - POST /auth/login
  - POST /auth/logout
  - GET /api/auth/me
  - POST /api/auth/register
  - POST /api/auth/login
- Cars
  - GET /cars
  - GET /cars/{id}
  - GET /api/cars
  - GET /api/cars/{id}
  - GET /api/cars/latest
- Services
  - GET /services
  - GET /api/services
- Parts
  - GET /parts
  - GET /api/parts
- Service Centers
  - GET /service-centers
  - GET /api/service-centers
- Profile (requires Authorization: Bearer <token>)
  - GET /profile
  - PUT /profile
  - GET /api/profile
  - PUT /api/profile

## Environment

Values are optional and controlled via .env.

- BACKEND_PORT: default 3001
- BACKEND_HOST: default 0.0.0.0
- ALLOW_ORIGINS: comma-separated allowed origins (default http://localhost:3000)

CORS will allow the React origin from env.

## Run (dev)

1) Create venv and install
   pip install -r requirements.txt

2) Start server (two options):
   uvicorn backend.main:app --host 0.0.0.0 --port 3001 --reload
   # or package app
   uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload

Open docs at http://localhost:3001/docs
Health: GET http://localhost:3001/
