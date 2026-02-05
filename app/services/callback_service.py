import requests
from app.config import GUVI_CALLBACK_URL
from app.models.schemas import ExtractedIntelligence

def send_guvi_callback(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: str
) -> dict:
    """Send final results to GUVI evaluation endpoint."""
    
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": {
            "bankAccounts": intelligence.bankAccounts,
            "upiIds": intelligence.upiIds,
            "phishingLinks": intelligence.phishingLinks,
            "phoneNumbers": intelligence.phoneNumbers,
            "suspiciousKeywords": intelligence.suspiciousKeywords
        },
        "agentNotes": agent_notes
    }
    
    print(f"📤 Sending callback to GUVI: {payload}")
    
    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Callback response: {response.status_code}")
        return {"status": "sent", "response_code": response.status_code}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Callback failed: {e}")
        return {"status": "failed", "error": str(e)}