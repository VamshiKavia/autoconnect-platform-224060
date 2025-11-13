# Backend (FastAPI)

Provides mock endpoints for the car company app: auth (stub), cars, services, parts, service centers, and user profile. CORS is configured to allow the React frontend.

## Run

1) Create and activate a virtual env (recommended)
2) Install dependencies:

pip install -r backend/requirements.txt

3) Set environment variables (see .env.example):

- BACKEND_PORT (default 3001)
- FRONTEND_URL (default http://localhost:3000)

4) Start server:

uvicorn backend.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-3001} --reload

Open http://localhost:3001/docs for API docs.

## Endpoints

- GET /            -> health
- POST /auth/login -> returns mock bearer token
- POST /auth/logout
- GET /cars
- GET /services
- GET /parts
- GET /service-centers
- GET /profile      (requires Authorization: Bearer <token>)
- PUT /profile      (requires Authorization: Bearer <token>)
