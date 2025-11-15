# Ocean Motors Backend (FastAPI)

Mock FastAPI backend serving endpoints for the React frontend.

## Run

- Create and configure environment variables as needed
  - FRONTEND_URL=http://localhost:3000 (for CORS)
  - BACKEND_PORT=3001
- Install dependencies:
  - pip install fastapi uvicorn pydantic python-dotenv
- Start:
  - uvicorn app.main:app --host 0.0.0.0 --port 3001

OpenAPI docs at /docs

## Endpoints (subset)

- GET /                  - Health
- POST /api/auth/login   - Mock login
- POST /api/auth/register- Mock register
- GET /api/cars          - Latest cars
- GET /api/services      - Services
- GET /api/parts         - Parts
- GET /api/service-centers - Service centers
- GET /api/profile       - Profile (requires Bearer mock-token)
- PUT /api/profile       - Update profile (requires Bearer mock-token)

CORS allowed origin defaults to http://localhost:3000 (configurable).
