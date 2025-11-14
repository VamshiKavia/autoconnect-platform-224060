from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import os

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_TITLE = "Ocean Motors API"
APP_DESCRIPTION = "Mock API for Ocean Motors frontend vertical slice. Provides auth, cars, services, parts, service centers, and profile."
APP_VERSION = "0.1.0"

tags_metadata = [
    {"name": "health", "description": "Health and service status"},
    {"name": "auth", "description": "Authentication endpoints"},
    {"name": "cars", "description": "Latest car launches"},
    {"name": "services", "description": "Service catalog"},
    {"name": "parts", "description": "Spare parts catalog"},
    {"name": "centers", "description": "Service centers listing"},
    {"name": "profile", "description": "User profile management"},
]

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION, openapi_tags=tags_metadata)

# CORS
allowed_origins = [o.strip() for o in (os.getenv("ALLOWED_ORIGINS") or "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory "DB"
USERS = {}  # email -> {email,name,password,phone,bio,created_at}
from datetime import datetime

# Models
class LoginIn(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=4, description="User password")

class RegisterIn(LoginIn):
    name: str = Field(..., min_length=1, description="Full name")

class TokenOut(BaseModel):
    access_token: str = Field(..., description="Bearer token")
    token_type: str = Field(default="bearer", description="Token type")
    user: Optional[dict] = Field(default=None, description="User info")

class Car(BaseModel):
    id: int
    name: str
    type: str
    year: int
    price: float
    is_new: bool = True

class ServiceItem(BaseModel):
    id: str
    name: str
    price: float
    duration_min: int

class PartItem(BaseModel):
    id: str
    name: str
    sku: str
    price: float

class ServiceCenter(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float
    phone: str

class Profile(BaseModel):
    email: EmailStr
    name: Optional[str] = ""
    phone: Optional[str] = ""
    bio: Optional[str] = ""
    created_at: Optional[str] = None

# Helpers
def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Very simple token check for mock; accepts 'Bearer mock-token'."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1].strip()
    if token != "mock-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token

# Routes

@app.get("/", tags=["health"], summary="Healthcheck", description="Returns 200 OK if service is up")
def health():
    return {"status": "ok", "service": APP_TITLE, "version": APP_VERSION}

@app.post("/api/auth/login", response_model=TokenOut, tags=["auth"], summary="Login", description="Authenticate user and return a mock token")
def login(payload: LoginIn):
    user = USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": "mock-token", "token_type": "bearer", "user": {"email": user["email"], "name": user["name"]}}

@app.post("/api/auth/register", response_model=TokenOut, tags=["auth"], summary="Register", description="Create a new user and return token")
def register(payload: RegisterIn):
    if payload.email in USERS:
        raise HTTPException(status_code=409, detail="Account already exists")
    USERS[payload.email] = {
        "email": payload.email,
        "name": payload.name,
        "password": payload.password,
        "phone": "",
        "bio": "",
        "created_at": datetime.utcnow().isoformat(),
    }
    return {"access_token": "mock-token", "token_type": "bearer", "user": {"email": payload.email, "name": payload.name}}

@app.get("/api/cars", response_model=List[Car], tags=["cars"], summary="Latest cars", description="List latest car launches")
def get_cars():
    return [
        Car(id=1, name="Aerexa", type="Sedan", year=2025, price=28990, is_new=True),
        Car(id=2, name="Straton Sport", type="Coupe", year=2025, price=41990, is_new=True),
        Car(id=3, name="Azure GT", type="Coupe", year=2024, price=48990, is_new=False),
    ]

@app.get("/api/services", response_model=List[ServiceItem], tags=["services"], summary="Service catalog", description="List available services")
def get_services():
    return [
        ServiceItem(id="svc1", name="Oil Change", price=69, duration_min=30),
        ServiceItem(id="svc2", name="Brake Inspection", price=99, duration_min=45),
        ServiceItem(id="svc3", name="AC Service", price=129, duration_min=60),
    ]

@app.get("/api/parts", response_model=List[PartItem], tags=["parts"], summary="Spare parts", description="List parts")
def get_parts():
    return [
        PartItem(id="p1", name="Air Filter", sku="AF-001", price=19.99),
        PartItem(id="p2", name="Brake Pads", sku="BP-101", price=49.99),
        PartItem(id="p3", name="Spark Plug", sku="SP-301", price=9.99),
    ]

@app.get("/api/service-centers", response_model=List[ServiceCenter], tags=["centers"], summary="Service centers", description="List authorized service centers")
def get_centers():
    return [
        ServiceCenter(id="c1", name="Ocean Service - JP Nagar", address="JP Nagar, Bengaluru", lat=12.90, lng=77.58, phone="+91-80-1234-5678"),
        ServiceCenter(id="c2", name="Ocean Service - Banashankari", address="2nd Stage, Bengaluru", lat=12.93, lng=77.55, phone="+91-80-9876-5432"),
    ]

@app.get("/api/profile", response_model=Profile, tags=["profile"], summary="Get profile", description="Return profile for current user")
def get_profile(token: str = Depends(verify_token)):
    # Return the first registered user for mock demo, or a default demo
    if USERS:
        user = next(iter(USERS.values()))
        return Profile(email=user["email"], name=user["name"], phone=user["phone"], bio=user["bio"], created_at=user["created_at"])
    return Profile(email="demo@example.com", name="Demo User", phone="", bio="", created_at=datetime.utcnow().isoformat())

@app.put("/api/profile", response_model=Profile, tags=["profile"], summary="Update profile", description="Update current user profile")
def update_profile(profile: Profile, token: str = Depends(verify_token)):
    user = USERS.get(profile.email)
    if user:
        user["name"] = profile.name or user["name"]
        user["phone"] = profile.phone or ""
        user["bio"] = profile.bio or ""
        return Profile(email=user["email"], name=user["name"], phone=user["phone"], bio=user["bio"], created_at=user["created_at"])
    # If not existing, upsert minimal
    USERS[profile.email] = {
        "email": profile.email,
        "name": profile.name or "",
        "password": "password",
        "phone": profile.phone or "",
        "bio": profile.bio or "",
        "created_at": profile.created_at or datetime.utcnow().isoformat(),
    }
    u = USERS[profile.email]
    return Profile(email=u["email"], name=u["name"], phone=u["phone"], bio=u["bio"], created_at=u["created_at"])
