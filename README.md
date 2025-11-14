# FastAPI Backend - Car Company App

This FastAPI server provides mock/in-memory endpoints for the car company application.

## Features

- Health and Docs
  - GET / (health with metadata)
  - GET /docs/guide
  - GET /api/docs/websocket
- Auth endpoints (mock token, also mirrored without /api for convenience)
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
- Services and Parts
  - GET /services
  - GET /parts
  - GET /api/services
  - GET /api/parts
- Service Centers
  - GET /service-centers
  - GET /api/service-centers
- User Profile (mock)
  - GET /profile
  - PUT /profile
  - GET /api/profile
  - PUT /api/profile
- CORS enabled for http://localhost:3000 by default via ALLOW_ORIGINS env.

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
