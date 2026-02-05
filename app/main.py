from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse
from app.config import SECRET_API_KEY
from app.models.guvi_schemas import GuviRequest, GuviResponse
from app.services.guvi_service import process_guvi_event
from app.dashboard import get_dashboard_html

app = FastAPI(title="Scam Honeypot API")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Web Dashboard"""
    return get_dashboard_html()

@app.post("/api/guvi/honeypot", response_model=GuviResponse)
async def honeypot_endpoint(
    request: GuviRequest,
    api_key: str = Depends(verify_api_key)
):
    """GUVI Honeypot Endpoint"""
    reply = process_guvi_event(request.dict())
    return GuviResponse(reply=reply)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "honeypot"}