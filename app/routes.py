from fastapi import APIRouter
from app.models.schemas import (
    HoneypotRequest, 
    HoneypotResponse,
    MessageRequest,
    AnalysisResponse
)
from app.services.honeypot_agent import (
    process_honeypot_request,
    get_session_state,
    reset_session
)
from app.services.ai_service import analyze_message
import json

router = APIRouter()

@router.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(request: HoneypotRequest):
    """
    Main Honeypot API Endpoint (GUVI Format)
    
    Accepts scam messages and returns AI agent responses.
    """
    result = process_honeypot_request(request)
    return result

@router.get("/session/{session_id}")
def get_session(session_id: str):
    """Get current session state (for debugging)."""
    return get_session_state(session_id)

@router.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Reset/delete a session."""
    return reset_session(session_id)

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_scam(request: MessageRequest):
    """Basic scam analysis (non-honeypot)."""
    result = analyze_message(request.message)
    return json.loads(result)

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "Agentic Honeypot API"}