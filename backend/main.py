import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

# ---- Environment config ----
# Do not hardcode secrets. Use environment variables for configuration only.
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "3001"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
# Align with README: ALLOW_ORIGINS env (comma-separated), default to localhost:3000
_allow_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _allow_origins.split(",") if o.strip()]

SERVICE_NAME = "car-company-backend"
APP_VERSION = "0.1.0"

openapi_tags = [
    {"name": "Auth", "description": "Authentication and user identity endpoints"},
    {"name": "Cars", "description": "Car listings and details"},
    {"name": "Services", "description": "Service catalog"},
    {"name": "Parts", "description": "Spare parts catalog"},
    {"name": "Service Centers", "description": "Service center locations"},
    {"name": "Profile", "description": "User profile management"},
    {"name": "Docs", "description": "API and WebSocket documentation"},
    {"name": "Health", "description": "Health and service status"},
]

app = FastAPI(
    title="Car Company API",
    description="FastAPI backend for the Ocean Professional themed car company app. Mock data only.",
    version=APP_VERSION,
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
cars: List[Dict[str, Any]] = [
    {"id": 1, "name": "Aerexa", "type": "Sedan", "year": 2025, "price": 28990, "is_new": True},
    {"id": 2, "name": "Straton Sport", "type": "Coupe", "year": 2025, "price": 41990, "is_new": True},
    {"id": 3, "name": "Azure GT", "type": "Coupe", "year": 2024, "price": 48990, "is_new": False},
]

services: List[Dict[str, Any]] = [
    {"id": "svc1", "name": "Oil Change", "price": 69, "duration_min": 30},
    {"id": "svc2", "name": "Brake Inspection", "price": 99, "duration_min": 45},
    {"id": "svc3", "name": "AC Service", "price": 129, "duration_min": 60},
]

parts: List[Dict[str, Any]] = [
    {"id": "p1", "name": "Air Filter", "sku": "AF-001", "price": 19.99},
    {"id": "p2", "name": "Brake Pads", "sku": "BP-101", "price": 49.99},
    {"id": "p3", "name": "Spark Plug", "sku": "SP-301", "price": 9.99},
]

service_centers: List[Dict[str, Any]] = [
    {
        "id": "sc1",
        "name": "Pavan Hyundai Signature Car Showroom - Kanakapura Road",
        "address": "13/2/1, Kanakapura Main Rd, Bengaluru",
        "lat": 12.894965115435244,
        "lng": 77.56785585085888,
        "phone": "+91-80-0000-0001",
    },
    {
        "id": "sc2",
        "name": "Nandi Toyota - Sales - Bannerghatta Road",
        "address": "Bannerghatta Rd, Bengaluru",
        "lat": 12.932031230477637,
        "lng": 77.59790932032661,
        "phone": "+91-80-0000-0002",
    },
]

# In-memory users and tokens (mock)
# email -> {password, name}
mock_users: Dict[str, Dict[str, str]] = {"demo@example.com": {"password": "Password123!", "name": "Demo User"}}
# token -> email
token_store: Dict[str, str] = {}
# profile storage (single structure, but we will update per-authenticated email on the fly)
mock_user_profile: Dict[str, Any] = {
    "email": "demo@example.com",
    "name": "Demo User",
    "phone": "",
    "bio": "",
    "created_at": datetime.utcnow().isoformat(),
}

# ---- Pydantic models ----
class RegisterPayload(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")
    name: str = Field(..., description="Full name")


class LoginPayload(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="User password")


class LogoutPayload(BaseModel):
    authorization: Optional[str] = Field(None, description="Optional Authorization header value to invalidate")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Bearer token to be used for Authorization header")
    token_type: str = Field("bearer", description="Token type, typically 'bearer'")
    user: Dict[str, Any] = Field(..., description="Basic user info")


class ProfileModel(BaseModel):
    email: EmailStr = Field(..., description="User email (read-only)")
    name: Optional[str] = Field("", description="User name")
    phone: Optional[str] = Field("", description="Phone number")
    bio: Optional[str] = Field("", description="Short bio")
    created_at: Optional[str] = Field(None, description="ISO timestamp of creation")


# ---- Helpers ----
def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


def get_bearer_token(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    return _extract_bearer(authorization)


def require_user(token: Optional[str] = Depends(get_bearer_token)) -> str:
    if not token or token not in token_store:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return token_store[token]


# ---- Health and docs helpers ----
# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health check", description="Simple healthcheck endpoint returning status ok and metadata.")
def health():
    """
    Root health endpoint.

    Returns:
        JSON with status, service name, and current time string.
    """
    return {"status": "ok", "service": SERVICE_NAME, "time": datetime.utcnow().isoformat()}


# PUBLIC_INTERFACE
@app.get(
    "/docs/guide",
    tags=["Docs"],
    summary="Documentation guide",
    description="Provides a brief note on WebSocket availability and docs navigation.",
)
def docs_guide():
    """
    API Docs helper.

    Returns:
        JSON containing websocket note and quick links.
    """
    return {
        "websocket": "No WebSocket endpoints available yet.",
        "note": "Use /docs for OpenAPI. Authentication uses simple mock bearer tokens.",
    }


# PUBLIC_INTERFACE
@app.get(
    "/api/docs/websocket",
    tags=["Docs"],
    summary="WebSocket usage note",
    description="This project currently has no WebSocket endpoints. If added, they will be documented here.",
)
def websocket_docs():
    """Provide project-level usage note for WebSockets."""
    return {"websocket": "No WebSocket endpoints available yet."}


# ---- Auth endpoints ----
def _issue_mock_token(email: str) -> str:
    # Create a deterministic but unique-enough mock token per email and time
    # Note: not a secret; purely for mock/testing
    token = f"mocktoken-{email}-{int(datetime.utcnow().timestamp())}"
    token_store[token] = email
    return token


# PUBLIC_INTERFACE
@app.post(
    "/auth/register",
    tags=["Auth"],
    response_model=TokenResponse,
    summary="Register new user (mock)",
    description="Registers a user in memory and returns a mock bearer token.",
)
def register_root(payload: RegisterPayload):
    """
    Register endpoint without /api prefix (for convenience in tests and development).
    """
    email = payload.email.lower().strip()
    # Idempotent behavior for tests: if user exists, still return a valid token
    if email not in mock_users:
        mock_users[email] = {"password": payload.password, "name": payload.name}
    token = _issue_mock_token(email)
    return {"access_token": token, "token_type": "bearer", "user": {"email": email, "name": mock_users[email]["name"]}}


# PUBLIC_INTERFACE
@app.post(
    "/api/auth/register",
    tags=["Auth"],
    response_model=TokenResponse,
    summary="Register new user (mock, /api)",
    description="Registers a user in memory and returns a mock bearer token.",
)
def register_api(payload: RegisterPayload):
    return register_root(payload)


# PUBLIC_INTERFACE
@app.post(
    "/auth/login",
    tags=["Auth"],
    response_model=TokenResponse,
    summary="Login (mock)",
    description="Accepts email and password and returns a mock bearer token.",
)
def login_root(payload: LoginPayload):
    """
    Login endpoint without /api prefix.
    """
    email = payload.email.lower().strip()
    user = mock_users.get(email)
    if not user or user.get("password") != payload.password:
        # If user does not exist, in a mock we can lazily create it to simplify demos
        mock_users[email] = {"password": payload.password, "name": email.split("@")[0].title()}
    token = _issue_mock_token(email)
    return {"access_token": token, "token_type": "bearer", "user": {"email": email, "name": mock_users[email]["name"]}}


# PUBLIC_INTERFACE
@app.post(
    "/api/auth/login",
    tags=["Auth"],
    response_model=TokenResponse,
    summary="Login (mock, /api)",
    description="Accepts email and password and returns a mock bearer token.",
)
def login_api(payload: LoginPayload):
    return login_root(payload)


# PUBLIC_INTERFACE
@app.post(
    "/auth/logout",
    tags=["Auth"],
    summary="Logout (mock)",
    description="Invalidates the provided token if present. Accepts optional {authorization: 'Bearer <token>'} in body.",
)
def logout_root(payload: LogoutPayload):
    """
    Logout endpoint: best-effort token invalidation based on provided authorization-like field.
    """
    token = _extract_bearer(payload.authorization) if payload and payload.authorization else None
    if token and token in token_store:
        token_store.pop(token, None)
    return {"ok": True}


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
    "/cars",
    tags=["Cars"],
    summary="List cars",
    description="Returns all cars.",
)
def list_cars_root():
    return cars


# PUBLIC_INTERFACE
@app.get(
    "/api/cars",
    tags=["Cars"],
    summary="List cars (/api)",
    description="Returns all cars.",
)
def list_cars_api():
    return cars


# PUBLIC_INTERFACE
@app.get(
    "/cars/{car_id}",
    tags=["Cars"],
    summary="Get car by id",
    description="Returns details for a single car by id.",
)
def get_car_root(car_id: int):
    for c in cars:
        if c["id"] == car_id:
            return c
    raise HTTPException(status_code=404, detail="Car not found")


# PUBLIC_INTERFACE
@app.get(
    "/api/cars/{car_id}",
    tags=["Cars"],
    summary="Get car by id (/api)",
    description="Returns details for a single car by id.",
)
def get_car_api(car_id: int):
    return get_car_root(car_id)


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


# ---- Services ----
# PUBLIC_INTERFACE
@app.get(
    "/services",
    tags=["Services"],
    summary="List services",
    description="Returns the list of available services.",
)
def list_services_root():
    return services


# PUBLIC_INTERFACE
@app.get(
    "/api/services",
    tags=["Services"],
    summary="List services (/api)",
    description="Returns the list of available services.",
)
def list_services_api():
    return services


# ---- Parts ----
# PUBLIC_INTERFACE
@app.get(
    "/parts",
    tags=["Parts"],
    summary="List parts",
    description="Returns the list of available spare parts.",
)
def list_parts_root():
    return parts


# PUBLIC_INTERFACE
@app.get(
    "/api/parts",
    tags=["Parts"],
    summary="List parts (/api)",
    description="Returns the list of available spare parts.",
)
def list_parts_api():
    return parts


# ---- Service Centers ----
# PUBLIC_INTERFACE
@app.get(
    "/service-centers",
    tags=["Service Centers"],
    summary="List service centers",
    description="Returns service center locations (mock) suitable for map display.",
)
def list_service_centers_root():
    return service_centers


# PUBLIC_INTERFACE
@app.get(
    "/api/service-centers",
    tags=["Service Centers"],
    summary="List service centers (/api)",
    description="Returns service center locations (mock) suitable for map display.",
)
def list_service_centers_api():
    return service_centers


# ---- Profile ----
# PUBLIC_INTERFACE
@app.get(
    "/profile",
    tags=["Profile"],
    response_model=ProfileModel,
    summary="Get profile",
    description="Returns the current user's profile (mock). Requires Authorization bearer token.",
)
def get_profile_root(current_email: str = Depends(require_user)):
    """
    In a multi-user world we'd return per-user data, here we return a mock profile
    and override the email and name based on the authenticated user.
    """
    result = dict(mock_user_profile)
    result["email"] = current_email
    result["name"] = mock_users.get(current_email, {}).get("name", result.get("name"))
    return result


# PUBLIC_INTERFACE
@app.get(
    "/api/profile",
    tags=["Profile"],
    response_model=ProfileModel,
    summary="Get profile (/api)",
    description="Returns the current user's profile (mock). Requires Authorization bearer token.",
)
def get_profile_api(current_email: str = Depends(require_user)):
    return get_profile_root(current_email)


# PUBLIC_INTERFACE
@app.put(
    "/profile",
    tags=["Profile"],
    response_model=ProfileModel,
    summary="Update profile",
    description="Updates the user profile in memory. Requires Authorization bearer token.",
)
def update_profile_root(payload: ProfileModel, current_email: str = Depends(require_user)):
    # Ensure the email cannot be changed away from the authenticated identity
    updated = payload.dict()
    updated["email"] = current_email
    # Persist to in-memory profile
    mock_user_profile.update(updated)
    # Also keep name in users dict for consistency
    if "name" in updated:
        if current_email not in mock_users:
            mock_users[current_email] = {"password": "Password123!", "name": updated["name"] or ""}
        else:
            mock_users[current_email]["name"] = updated["name"] or mock_users[current_email].get("name", "")
    return updated


# PUBLIC_INTERFACE
@app.put(
    "/api/profile",
    tags=["Profile"],
    response_model=ProfileModel,
    summary="Update profile (/api)",
    description="Updates the user profile in memory. Requires Authorization bearer token.",
)
def update_profile_api(payload: ProfileModel, current_email: str = Depends(require_user)):
    return update_profile_root(payload, current_email)
