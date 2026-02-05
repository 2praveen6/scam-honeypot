import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

# -----------------------------
# Config & Services
# -----------------------------
from app.config import SECRET_API_KEY
from app.models.guvi_schemas import GuviRequest, GuviResponse
from app.models.scan_schemas import ScanRequest, ScanResponse
from app.services.guvi_service import process_guvi_event
from app.services.scan_service import scan_message_simple
from app.dashboard import get_dashboard_html

# -----------------------------
# Database
# -----------------------------
from app.db import engine
from app.db_models import Base

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="Scam Honeypot API",
    version="1.0"
)

# -----------------------------
# Create DB tables on startup
# -----------------------------
@app.on_event("startup")
def startup():
    try:
        print("📦 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database ready")
    except Exception as e:
        print("❌ DB Startup Error:", e)


# -----------------------------
# API Key Security
# -----------------------------
api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)

def verify_api_key(
    api_key: str = Security(api_key_header)
):
    if api_key != SECRET_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    return api_key


# -----------------------------
# Dashboard UI
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return get_dashboard_html()


# -----------------------------
# Scam Detector UI
# -----------------------------
@app.get("/detector")
async def scam_detector_ui():
    file_path = os.path.join(
        "app",
        "templates",
        "scam_detector.html"
    )

    if not os.path.exists(file_path):
        return HTMLResponse(
            "<h2>Detector UI not found</h2>",
            status_code=404
        )

    return FileResponse(file_path)


# -----------------------------
# Honeypot API
# -----------------------------
@app.post(
    "/api/guvi/honeypot",
    response_model=GuviResponse
)
async def honeypot_endpoint(
    request: GuviRequest,
    api_key: str = Depends(verify_api_key)
):
    reply = process_guvi_event(
        request.dict()
    )
    return GuviResponse(reply=reply)


# -----------------------------
# Simple Scan API
# -----------------------------
@app.post(
    "/api/scan",
    response_model=ScanResponse
)
async def scan_message(
    request: ScanRequest
):
    result = scan_message_simple(
        request.message
    )
    return result


# -----------------------------
# Health Check (Railway uses this)
# -----------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "honeypot",
        "version": "1.0"
    }
