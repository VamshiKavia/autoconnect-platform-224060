import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

# Environment configuration
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "3001"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

openapi_tags = [
    {"name": "health", "description": "Healthcheck and docs"},
    {"name": "auth", "description": "Authentication endpoints (stub/mock)"},
    {"name": "cars", "description": "Latest car launches and catalog"},
    {"name": "services", "description": "Car services offering"},
    {"name": "parts", "description": "Spare parts listing"},
    {"name": "centers", "description": "Service center locations"},
    {"name": "profile", "description": "User profile management (mock)"},
]

app = FastAPI(
    title="Car Company Backend API",
    description="FastAPI backend providing mock data for cars, services, parts, service centers, and user profile. Includes stubbed auth.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS: allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock in-memory state
MOCK_USERS = {
    "demo@example.com": {
        "email": "demo@example.com",
        "name": "Demo User",
        "bio": "Enthusiast driver. Loves electric SUVs.",
        "phone": "+1-555-0100",
        "created_at": datetime.utcnow().isoformat(),
    }
}
MOCK_TOKENS = {}  # token -> email

MOCK_CARS = [
    {"id": "c1", "name": "Aquila X1", "type": "SUV", "year": 2025, "price": 54000, "is_new": True, "image": None},
    {"id": "c2", "name": "Triton S", "type": "Sedan", "year": 2025, "price": 38000, "is_new": True, "image": None},
    {"id": "c3", "name": "Vortex E", "type": "Hatchback", "year": 2024, "price": 29000, "is_new": False, "image": None},
]

MOCK_SERVICES = [
    {"id": "s1", "name": "Oil Change", "price": 89, "duration_min": 45},
    {"id": "s2", "name": "Tire Rotation", "price": 59, "duration_min": 30},
    {"id": "s3", "name": "Brake Inspection", "price": 129, "duration_min": 60},
]

MOCK_PARTS = [
    {"id": "p1", "name": "Air Filter", "sku": "AF-1001", "price": 25},
    {"id": "p2", "name": "Brake Pads", "sku": "BP-2040", "price": 120},
    {"id": "p3", "name": "Spark Plug", "sku": "SP-3009", "price": 18},
]

MOCK_CENTERS = [
    {
        "id": "sc1",
        "name": "Downtown Service Center",
        "address": "123 Main St, Metropolis",
        "lat": 40.7128,
        "lng": -74.0060,
        "phone": "+1-555-0111",
    },
    {
        "id": "sc2",
        "name": "Uptown Auto Care",
        "address": "456 Elm Ave, Metropolis",
        "lat": 40.7357,
        "lng": -74.1724,
        "phone": "+1-555-0222",
    },
]

# Models
class AuthRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password (not validated in mock)")

class AuthResponse(BaseModel):
    access_token: str = Field(..., description="Mock access token")
    token_type: str = Field(..., description="Token type, always 'bearer' for mock")

class Car(BaseModel):
    id: str
    name: str
    type: str
    year: int
    price: float
    is_new: bool
    image: Optional[str] = None

class Service(BaseModel):
    id: str
    name: str
    price: float
    duration_min: int

class Part(BaseModel):
    id: str
    name: str
    sku: str
    price: float

class ServiceCenter(BaseModel):
    id: str
    name: str
    address: str
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    phone: str

class ServiceCenterWithDistance(ServiceCenter):
    """Service center schema extended with distance in kilometers when geo params are provided."""
    distance_km: float = Field(..., description="Distance from query location in kilometers")

class Profile(BaseModel):
    email: str
    name: str
    bio: Optional[str] = ""
    phone: Optional[str] = ""
    created_at: Optional[str] = None


def get_current_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """
    Extract mock token from Authorization header and return user dict.
    Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    token = parts[1]
    email = MOCK_TOKENS.get(token)
    if not email or email not in MOCK_USERS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return MOCK_USERS[email]


# Routes

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Basic health check endpoint.")
def health_check():
    """Health status and environment summary."""
    return {"status": "ok", "service": "car-company-backend", "time": datetime.utcnow().isoformat()}

# PUBLIC_INTERFACE
@app.get("/docs/guide", tags=["health"], summary="WebSocket/Realtime usage note", description="No WebSocket endpoints in this project. This page exists as a placeholder per documentation standards.")
def ws_help():
    return {"websocket": False, "note": "No realtime endpoints. Use REST only."}

# PUBLIC_INTERFACE
@app.post("/auth/login", tags=["auth"], summary="Login (stub)", description="Accepts any email/password and returns a mock token.")
def login(payload: AuthRequest = Body(...)) -> AuthResponse:
    """Mock login endpoint. Creates a user if missing and returns a mock bearer token."""
    token = f"mocktoken-{hash(payload.email) % 1_000_000}"
    if payload.email not in MOCK_USERS:
        MOCK_USERS[payload.email] = {
            "email": payload.email,
            "name": payload.email.split("@")[0].title(),
            "bio": "",
            "phone": "",
            "created_at": datetime.utcnow().isoformat(),
        }
    MOCK_TOKENS[token] = payload.email
    return AuthResponse(access_token=token, token_type="bearer")

# PUBLIC_INTERFACE
@app.post("/api/auth/login", tags=["auth"], summary="Login (stub, API-prefixed mirror)", description="Mirror of /auth/login under /api prefix for frontend clients that auto-prefix with /api.")
def login_api_prefixed(payload: AuthRequest = Body(...)) -> AuthResponse:
    """Mirror route for API-prefixed login to support clients that prepend /api."""
    return login(payload)

class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password (not validated in mock)")
    name: str = Field(..., description="User display name")

class RegisterResponse(BaseModel):
    access_token: str = Field(..., description="Mock access token")
    token_type: str = Field(..., description="Token type")
    user: Profile = Field(..., description="Created user profile")

# PUBLIC_INTERFACE
@app.post("/auth/register", tags=["auth"], summary="Register (stub)", description="Creates a mock user record and returns token + user.")
def register(payload: RegisterRequest = Body(...)) -> RegisterResponse:
    """Mock register endpoint. Idempotent: creating an already-existing email returns existing profile."""
    email = payload.email.strip().lower()
    # Create user if not exists
    if email not in MOCK_USERS:
        MOCK_USERS[email] = {
            "email": email,
            "name": payload.name or email.split("@")[0].title(),
            "bio": "",
            "phone": "",
            "created_at": datetime.utcnow().isoformat(),
        }
    # Issue a new token on registration for convenience
    token = f"mocktoken-{hash(email) % 1_000_000}"
    MOCK_TOKENS[token] = email
    user = Profile(**MOCK_USERS[email])
    return RegisterResponse(access_token=token, token_type="bearer", user=user)

# PUBLIC_INTERFACE
@app.post("/api/auth/register", tags=["auth"], summary="Register (stub, API-prefixed mirror)", description="Mirror of /auth/register under /api prefix.")
def register_api_prefixed(payload: RegisterRequest = Body(...)) -> RegisterResponse:
    """Mirror route for API-prefixed register to support clients that prepend /api."""
    return register(payload)

# PUBLIC_INTERFACE
@app.post("/auth/logout", tags=["auth"], summary="Logout (stub)", description="Invalidates mock token.")
def logout(authorization: Optional[str] = Body(None, embed=True)):
    # Accept either Authorization header-like string in body or ignore for mock
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            MOCK_TOKENS.pop(token, None)
    return {"ok": True}

# PUBLIC_INTERFACE
@app.get("/cars", tags=["cars"], summary="List cars", description="Returns latest car launches and catalog.")
def list_cars() -> List[Car]:
    return [Car(**c) for c in MOCK_CARS]

# PUBLIC_INTERFACE
@app.get("/services", tags=["services"], summary="List services", description="Returns available car services.")
def list_services() -> List[Service]:
    return [Service(**s) for s in MOCK_SERVICES]

# PUBLIC_INTERFACE
@app.get("/parts", tags=["parts"], summary="List parts", description="Returns available spare parts.")
def list_parts() -> List[Part]:
    return [Part(**p) for p in MOCK_PARTS]

# PUBLIC_INTERFACE
@app.get(
    "/service-centers",
    tags=["centers"],
    summary="List service centers",
    description=(
        "Returns service centers with optional text and geospatial filters.\n\n"
        "Query parameters:\n"
        "- q: substring match on name or address (case-insensitive)\n"
        "- lat, lng: coordinates to compute distance (Haversine)\n"
        "- radius_km: filter centers within this radius (km)\n"
        "- limit: max number of items to return (default 50, max 200)\n\n"
        "When lat/lng/radius are provided, each item will include distance_km."
    ),
    responses={
        200: {"description": "List of service centers (optionally filtered)."},
        400: {"description": "Invalid parameters"},
    },
)
def list_service_centers(
    q: Optional[str] = Query(default=None, description="Substring to match against name or address"),
    lat: Optional[float] = Query(default=None, description="Latitude for distance filter"),
    lng: Optional[float] = Query(default=None, description="Longitude for distance filter"),
    radius_km: Optional[float] = Query(default=None, description="Radius in kilometers to filter centers (max 100)"),
    limit: Optional[int] = Query(default=50, description="Max number of results (default 50, max 200)"),
):
    """
    PUBLIC_INTERFACE
    Returns service centers with optional filters and distance calculation.

    - If no parameters are provided, returns all centers (backward compatible).
    - If q is provided, performs a case-insensitive substring match on name and address.
    - If lat/lng are provided:
        - Optionally filter by radius_km (capped to 100 km).
        - Include distance_km in the response items.
    - limit is capped to 200 to prevent excessively large responses.
    """
    # Basic validation
    if limit is None:
        limit = 50
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be a positive integer")
    if limit > 200:
        limit = 200

    use_geo = (lat is not None) or (lng is not None) or (radius_km is not None)
    if use_geo:
        # Require both lat and lng when any geo param is supplied
        if lat is None or lng is None:
            raise HTTPException(status_code=400, detail="lat and lng are required when using geo filters")
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
            raise HTTPException(status_code=400, detail="lat must be [-90,90] and lng must be [-180,180]")
        if radius_km is not None:
            if radius_km <= 0:
                raise HTTPException(status_code=400, detail="radius_km must be > 0")
            # Cap radius to 100 km
            if radius_km > 100:
                radius_km = 100.0

    # Filter by q if provided
    def matches_query(center: Dict[str, Any]) -> bool:
        if not q:
            return True
        s = q.strip().lower()
        return (s in (center.get("name") or "").lower()) or (s in (center.get("address") or "").lower())

    filtered = [c for c in MOCK_CENTERS if matches_query(c)]

    # If geo requested, compute distances and optionally filter by radius
    result: List[Dict[str, Any]] = []
    if use_geo:
        from math import radians, sin, cos, asin, sqrt

        def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            # Earth radius in kilometers
            R = 6371.0
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            return R * c

        for c in filtered:
            d_km = haversine_km(lat, lng, float(c["lat"]), float(c["lng"]))
            if radius_km is not None and d_km > radius_km:
                continue
            item = {**c, "distance_km": round(d_km, 3)}
            result.append(item)

        # Sort by nearest when geo used
        result.sort(key=lambda x: x["distance_km"])
        # Apply limit
        result = result[:limit]
        # Return typed models with distance
        return [ServiceCenterWithDistance(**r) for r in result]

    # Non-geo path: apply limit and return legacy schema
    return [ServiceCenter(**c) for c in filtered[:limit]]

# PUBLIC_INTERFACE
@app.get("/profile", tags=["profile"], summary="Get profile", description="Returns current user's profile. Requires mock Authorization bearer token.")
def get_profile(user: Dict[str, Any] = Depends(get_current_user)) -> Profile:
    return Profile(**user)

# PUBLIC_INTERFACE
@app.put("/profile", tags=["profile"], summary="Update profile", description="Updates current user's profile. Requires mock Authorization bearer token.")
def update_profile(profile: Profile, user: Dict[str, Any] = Depends(get_current_user)) -> Profile:
    # Update allowed fields only
    user["name"] = profile.name
    user["bio"] = profile.bio
    user["phone"] = profile.phone
    MOCK_USERS[user["email"]] = user
    return Profile(**user)
