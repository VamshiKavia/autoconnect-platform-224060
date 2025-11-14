# FastAPI Backend - Car Company App

This FastAPI server provides mock/in-memory endpoints for the car company application.

## Features

- Auth endpoints (mock token)
  - POST /api/auth/register
  - POST /api/auth/login
  - GET /api/auth/me
- Cars
  - GET /api/cars/latest
  - GET /api/cars
  - GET /api/cars/{id}
- Services and Parts
  - GET /api/services
  - GET /api/parts
- Service Centers
  - GET /api/service-centers
- User Profile (mock)
  - GET /api/profile
  - PUT /api/profile
- CORS enabled for http://localhost:3000 by default

## Environment

Values are optional and controlled via .env.

- BACKEND_PORT: default 3001
- BACKEND_HOST: default 0.0.0.0
- ALLOW_ORIGINS: comma-separated allowed origins (default http://localhost:3000)

See .env.example.

## Run

1) Create virtualenv and install:
   pip install -r backend/requirements.txt

2) Start server:
   uvicorn backend.main:app --host 0.0.0.0 --port 3001 --reload

Open docs at http://localhost:3001/docs

Health: GET http://localhost:3001/
