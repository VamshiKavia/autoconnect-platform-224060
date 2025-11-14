# FastAPI Backend - Ocean Motors (Mock)

Mock backend with CORS for the React SPA. Implements minimal endpoints:

- GET / -> health
- POST /api/auth/login
- POST /api/auth/register
- GET /api/cars
- GET /api/services
- GET /api/parts
- GET /api/service-centers
- GET /api/profile (requires Authorization: Bearer <token>)
- PUT /api/profile (requires Authorization)

Run (dev):
- Create .env from .env.example
- pip install -r requirements.txt
- uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
