import os
import json
import asyncio
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Security, WebSocket, WebSocketDisconnect
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse, FileResponse

from dotenv import load_dotenv
load_dotenv()

# 🔐 Config
from app.config import SECRET_API_KEY

# 🧠 Schemas & Services
from app.models.guvi_schemas import GuviRequest, GuviResponse
from app.models.scan_schemas import ScanRequest, ScanResponse
from app.services.guvi_service import process_guvi_event
from app.services.scan_service import scan_message_simple

# 📊 Dashboard
from app.dashboard import get_dashboard_html

# 🗄️ Database
from app.db import engine
from app.db_models import Base


# 🚀 App
app = FastAPI(title="Scam Honeypot API")

# ===============================
# 🔴 REAL-TIME DASHBOARD SOCKETS
# ===============================
active_connections: List[WebSocket] = []


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# 🧠 Auto-create DB tables
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# 🔐 API Key Security
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


# 🌐 Scam Detector UI
@app.get("/detector")
async def scam_detector_ui():
    return FileResponse("app/templates/scam_detector.html")


# 📊 Dashboard UI
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return get_dashboard_html()


# 🔍 PUBLIC SCAN API (no API key)
@app.post("/api/scan", response_model=ScanResponse)
async def scan_api(request: ScanRequest):
    return scan_message_simple(request.message)


# 🤖 Honeypot API (secured)
@app.post("/api/guvi/honeypot", response_model=GuviResponse)
async def honeypot_endpoint(
    request: GuviRequest,
    api_key: str = Depends(verify_api_key)
):
    reply = await process_guvi_event(request.dict())
    return GuviResponse(reply=reply)


# ❤️ Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
