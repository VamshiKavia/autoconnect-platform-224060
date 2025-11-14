import os
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---- Environment config ----
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "3001"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
_allow_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _allow_origins.split(",") if o.strip()]

# ---- App init with OpenAPI metadata ----
openapi_tags = [
    {"name": "Auth", "description": "Authentication and user identity endpoints"},
    {"name": "Cars", "description": "Car listings and details"},
    {"name": "Services", "description": "Service catalog"},
    {"name": "Parts", "description": "Spare parts catalog"},
    {"name": "Service Centers", "description": "Service center locations"},
    {"name": "Profile", "description": "User profile management"},
    {"name": "Docs", "description": "API and WebSocket documentation"},
]

app = FastAPI(
    title="Car Company API",
    description="FastAPI backend for the Ocean Professional themed car company app. Mock data only.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Mock data stores ----
cars = [
    {"id": 1, "name": "Aerexa", "type": "Sedan", "year": 2025, "price": 28990, "is_new": True},
    {"id": 2, "name": "Straton Sport", "type": "Coupe", "year": 2025, "price": 41990, "is_new": True},
    {"id": 3, "name": "Azure GT", "type": "Coupe", "year": 2024, "price": 48990, "is_new": False},
]

services = [
    {"id": "svc1", "name": "Oil Change", "price": 69, "duration_min": 30},
    {"id": "svc2", "name": "Brake Inspection", "price": 99, "duration_min": 45},
    {"id": "svc3", "name": "AC Service", "price": 129, "duration_min": 60},
]

parts = [
    {"id": "p1", "name": "Air Filter", "sku": "AF-001", "price": 19.99},
    {"id": "p2", "name": "Brake Pads", "sku": "BP-101", "price": 49.99},
    {"id": "p3", "name": "Spark Plug", "sku": "SP-301", "price": 9.99},
]

service_centers = [
    {
        "id": "sc1",
        "brand": "HYUNDAI",
        "name": "Pavan Hyundai Signature Car Showroom - Kanakapura Road",
        "lat": 12.894965115435244,
        "lng": 77.56785585085888,
        "address": "13/2/1, Kanakapura Main Rd, Bengaluru",
    },
    {
        "id": "sc2",
        "brand": "TOYOTA",
        "name": "Nandi Toyota - Sales - Bannerghatta Road",
        "lat": 12.932031230477637,
        "lng": 77.59790932032661,
        "address": "Bannerghatta Rd, Bengaluru",
    },
]

# Mock user store (single user scenario)
mock_user_profile = {
    "email": "demo@example.com",
    "name": "Demo User",
    "phone": "",
    "bio": "",
    "created_at": "2024-01-01T00:00:00Z",
}
mock_users = {"demo@example.com": {"password": "password", "name": "Demo User"}}
# token -> email
token_store = {"mock-token": "demo@example.com"}


# ---- Pydantic models ----
class RegisterPayload(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")
    name: str = Field(..., description="Full name")


class LoginPayload(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Bearer token to be used for Authorization header")
    token_type: str = Field("bearer", description="Token type, typically 'bearer'")
    user: dict = Field(..., description="Basic user info")


class ProfileModel(BaseModel):
    email: str = Field(..., description="User email (read-only)")
    name: Optional[str] = Field("", description="User name")
    phone: Optional[str] = Field("", description="Phone number")
    bio: Optional[str] = Field("", description="Short bio")
    created_at: Optional[str] = Field(None, description="ISO timestamp of creation")


# ---- Helpers ----
def get_bearer_token(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


def require_user(token: Optional[str] = Depends(get_bearer_token)) -> str:
    if not token or token not in token_store:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return token_store[token]


# ---- Root and docs helpers ----
@app.get("/", tags=["Docs"], summary="Health check", description="Simple healthcheck endpoint returning status ok.")
def health():
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.get("/api/docs/websocket", tags=["Docs"], summary="WebSocket usage note", description="This project currently has no WebSocket endpoints. If added, they will be documented here with connection details and operation IDs.")
def websocket_docs():
    """Provide project-level usage note for WebSockets."""
    return {"websocket": "No WebSocket endpoints available yet."}


# ---- Auth endpoints ----
# PUBLIC_INTERFACE
@app.post(
    "/api/auth/register",
    tags=["Auth"],
    response_model=TokenResponse,
    summary="Register new user (mock)",
    description="Registers a user in memory and returns a mock bearer token.",
)
def register(payload: RegisterPayload):
    email = payload.email.lower().strip()
    if email in mock_users:
        raise HTTPException(status_code=409, detail="User already exists")
    mock_users[email] = {"password": payload.password, "name": payload.name}
    token_store["mock-token"] = email
    return {"access_token": "mock-token", "token_type": "bearer", "user": {"email": email, "name": payload.name}}


# PUBLIC_INTERFACE
@app.post(
    "/api/auth/login",
    tags=["Auth"],
    response_model=TokenResponse,
    summary="Login (mock)",
    description="Accepts email and password and returns a mock bearer token.",
)
def login(payload: LoginPayload):
    email = payload.email.lower().strip()
    user = mock_users.get(email)
    if not user or user.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_store["mock-token"] = email
    return {"access_token": "mock-token", "token_type": "bearer", "user": {"email": email, "name": user.get("name", "")}}


# PUBLIC_INTERFACE
@app.get(
    "/api/auth/me",
    tags=["Auth"],
    summary="Get current user",
    description="Returns the authenticated user's info using the provided bearer token.",
)
def auth_me(current_email: str = Depends(require_user)):
    return {"email": current_email, "name": mock_users.get(current_email, {}).get("name", "")}


# ---- Cars ----
# PUBLIC_INTERFACE
@app.get(
    "/api/cars/latest",
    tags=["Cars"],
    summary="Latest car launches",
    description="Returns the latest launched cars (subset of /cars).",
)
def get_latest_cars():
    latest = [c for c in cars if c.get("is_new")]
    return latest


# PUBLIC_INTERFACE
@app.get(
    "/api/cars",
    tags=["Cars"],
    summary="List cars",
    description="Returns all cars.",
)
def list_cars():
    return cars


# PUBLIC_INTERFACE
@app.get(
    "/api/cars/{car_id}",
    tags=["Cars"],
    summary="Get car by id",
    description="Returns details for a single car by id.",
)
def get_car(car_id: int):
    for c in cars:
        if c["id"] == car_id:
            return c
    raise HTTPException(status_code=404, detail="Car not found")


# ---- Services ----
# PUBLIC_INTERFACE
@app.get(
    "/api/services",
    tags=["Services"],
    summary="List services",
    description="Returns the list of available services.",
)
def list_services():
    return services


# ---- Parts ----
# PUBLIC_INTERFACE
@app.get(
    "/api/parts",
    tags=["Parts"],
    summary="List parts",
    description="Returns the list of available spare parts.",
)
def list_parts():
    return parts


# ---- Service Centers ----
# PUBLIC_INTERFACE
@app.get(
    "/api/service-centers",
    tags=["Service Centers"],
    summary="List service centers",
    description="Returns service center locations (mock) suitable for map display.",
)
def list_service_centers():
    return service_centers


# ---- Profile ----
# PUBLIC_INTERFACE
@app.get(
    "/api/profile",
    tags=["Profile"],
    response_model=ProfileModel,
    summary="Get profile",
    description="Returns the current user's profile (mock). Requires Authorization bearer token.",
)
def get_profile(current_email: str = Depends(require_user)):
    # in a multi-user world we'd return per-user data, here we return a static mock profile with email replaced
    result = dict(mock_user_profile)
    result["email"] = current_email
    result["name"] = mock_users.get(current_email, {}).get("name", result.get("name"))
    return result


# PUBLIC_INTERFACE
@app.put(
    "/api/profile",
    tags=["Profile"],
    response_model=ProfileModel,
    summary="Update profile",
    description="Updates the user profile in memory. Requires Authorization bearer token.",
)
def update_profile(payload: ProfileModel, current_email: str = Depends(require_user)):
    # Ensure the email cannot be changed
    updated = payload.dict()
    updated["email"] = current_email
    # Save minimal state
    mock_user_profile.update(updated)
    # Also keep name in users dict
    if "name" in updated and current_email in mock_users:
        mock_users[current_email]["name"] = updated["name"]
    return updated
