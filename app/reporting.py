import json
import requests
from datetime import datetime
from app.db import SessionLocal
from app.db_models import HoneypotSession

def report_to_cybercrime(session_id: str):
    """
    Report scammer to Indian Cybercrime Portal
    Note: This is a template - real API requires official access
    """
    db = SessionLocal()
    session = db.query(HoneypotSession).filter_by(session_id=session_id).first()
    
    if not session or not session.scam_detected:
        return False
    
    report_data = {
        "incident_type": "Financial Fraud",
        "platform": "WhatsApp/Telegram",
        "date_time": session.created_at.isoformat(),
        "evidence": {
            "upi_ids": json.loads(session.upi_ids),
            "phone_numbers": json.loads(session.phone_numbers),
            "phishing_links": json.loads(session.phishing_links),
            "total_messages": session.total_messages
        },
        "description": session.agent_notes,
        "reported_by": "Automated Honeypot System"
    }
    
    # For demo - log the report
    with open("scam_reports.json", "a") as f:
        json.dump(report_data, f)
        f.write("\n")
    
    db.close()
    return True