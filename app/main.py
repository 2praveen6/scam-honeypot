import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# SAFE IMPORTS
# -----------------------------
from app.config import SECRET_API_KEY
from app.models.guvi_schemas import GuviRequest, GuviResponse
from app.models.scan_schemas import ScanRequest, ScanResponse
from app.services.guvi_service import process_guvi_event
from app.services.scan_service import scan_message_simple
from app.dashboard import get_dashboard_html

app = FastAPI(title="Scam Honeypot API")


# -----------------------------
# HEALTHCHECK (FIRST — IMPORTANT)
# -----------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# -----------------------------
# API KEY SECURITY
# -----------------------------
api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != SECRET_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    return api_key


# -----------------------------
# DASHBOARD
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return get_dashboard_html()


# -----------------------------
# SCAM DETECTOR UI
# -----------------------------
@app.get("/detector")
async def scam_detector_ui():
    file_path = os.path.join(
        "app",
        "templates",
        "scam_detector.html"
    )
    return FileResponse(file_path)


# -----------------------------
# HONEYPOT ENDPOINT
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
# PUBLIC SCAN API
# -----------------------------
@app.post(
    "/api/scan",
    response_model=ScanResponse
)
async def scan_message(
    request: ScanRequest
):
    return scan_message_simple(
        request.message
    )
