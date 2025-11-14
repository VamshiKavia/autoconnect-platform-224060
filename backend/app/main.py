from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

APP_TITLE = "Ocean Motors API"
APP_DESCRIPTION = "Mock API for Ocean Motors frontend vertical slice. Provides auth, cars, services, parts, service centers, and profile."
APP_VERSION = "0.1.0"

tags_metadata = [
    {"name": "Health", "description": "Health and service status"},
    {"name": "Auth", "description": "Authentication endpoints"},
    {"name": "Cars", "description": "Latest car launches"},
    {"name": "Services", "description": "Service catalog"},
    {"name": "Parts", "description": "Spare parts catalog"},
    {"name": "Service Centers", "description": "Service centers listing"},
    {"name": "Profile", "description": "User profile management"},
]

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION, openapi_tags=tags_metadata)

# CORS from env
allowed_origins = [o.strip() for o in (os.getenv("ALLOW_ORIGINS") or "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple root for health
# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Healthcheck", description="Returns 200 OK if service is up")
def health():
    return {"status": "ok", "service": "ocean-motors-backend", "time": datetime.utcnow().isoformat()}

# Minimal notes for websocket docs
# PUBLIC_INTERFACE
@app.get("/api/docs/websocket", tags=["Health"], summary="WebSocket usage note", description="No websockets yet.")
def websocket_docs():
    return {"websocket": "No WebSocket endpoints available yet."}
