import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config
from app.config import SECRET_API_KEY

# Schemas
from app.models.guvi_schemas import GuviRequest, GuviResponse
from app.models.scan_schemas import ScanRequest, ScanResponse

# Services
from app.services.guvi_service import process_guvi_event
from app.services.scan_service import scan_message_simple

# Dashboard
from app.dashboard import get_dashboard_html

# Database
from app.db import engine
from app.db_models import Base


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI(title="Scam Honeypot API")


# --------------------------------------------------
# Startup → Create tables
# --------------------------------------------------
"""@app.on_event("startup")
def startup():
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready")"""


# --------------------------------------------------
# API Key Security
# --------------------------------------------------
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


# --------------------------------------------------
# Root → Needed for Railway health fallback
# --------------------------------------------------
@app.get("/")
async def root():
    return {"status": "running"}


# --------------------------------------------------
# Dashboard UI
# --------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return get_dashboard_html()


# --------------------------------------------------
# Scam Detector UI
# --------------------------------------------------
@app.get("/detector")
async def scam_detector_ui():
    file_path = os.path.join(
        "app",
        "templates",
        "scam_detector.html"
    )
    return FileResponse(file_path)


# --------------------------------------------------
# Honeypot Endpoint (FOR SUBMISSION)
# --------------------------------------------------
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


# --------------------------------------------------
# Public Scan API
# --------------------------------------------------
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


# --------------------------------------------------
# Health Check (CRITICAL FOR RAILWAY)
# --------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
