import json
import re
from datetime import datetime
from typing import Dict, List

from app.db import SessionLocal
from app.db_models import HoneypotSession
from app.utils.email_reporter import send_scam_report

# 🔴 Import active WebSocket connections
from app.main import active_connections


# =====================================================
# 📡 Broadcast to Live Dashboard
# =====================================================

async def broadcast_dashboard_update(data: Dict):
    """Send real-time update to dashboard clients"""
    dead_connections: List = []

    for ws in active_connections:
        try:
            await ws.send_text(json.dumps(data))
        except:
            dead_connections.append(ws)

    # Remove disconnected sockets
    for ws in dead_connections:
        active_connections.remove(ws)


# =====================================================
# 🧠 Process Honeypot Event
# =====================================================

async def process_guvi_event(event: dict) -> str:
    """Process incoming message and return honeypot reply"""

    session_id = event["sessionId"]
    message_text = event["message"]["text"]

    scam_found = False
    db = SessionLocal()

    try:
        # =============================
        # Get or Create Session
        # =============================
        session = db.query(HoneypotSession).filter_by(
            session_id=session_id
        ).first()

        if not session:
            session = HoneypotSession(
                session_id=session_id,
                scam_detected=False,
                total_messages=0,
                bank_accounts="[]",
                upi_ids="[]",
                phone_numbers="[]",
                phishing_links="[]",
                suspicious_keywords="[]"
            )
            db.add(session)

        # Update message count
        session.total_messages += 1

        # =============================
        # 🔎 Extract UPI IDs
        # =============================
        upi_pattern = r'\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b'
        upi_matches = re.findall(upi_pattern, message_text)

        if upi_matches:
            existing_upi = json.loads(session.upi_ids or "[]")
            session.upi_ids = json.dumps(
                list(set(existing_upi + upi_matches))
            )
            session.scam_detected = True
            scam_found = True

        # =============================
        # 📞 Extract Phone Numbers
        # =============================
        phone_pattern = r'\b[6-9]\d{9}\b'
        phone_matches = re.findall(phone_pattern, message_text)

        if phone_matches:
            existing_phones = json.loads(
                session.phone_numbers or "[]"
            )
            session.phone_numbers = json.dumps(
                list(set(existing_phones + phone_matches))
            )
            session.scam_detected = True
            scam_found = True

        # =============================
        # ⏱ Timestamp
        # =============================
        session.updated_at = datetime.utcnow()

        db.commit()

        # =============================
        # 📧 Send Email Report
        # =============================
        if scam_found:
            try:
                send_scam_report(
                    session_id=session_id,
                    message=message_text,
                    upi=", ".join(upi_matches) if upi_matches else "N/A",
                    phone=", ".join(phone_matches) if phone_matches else "N/A",
                    timestamp=str(datetime.utcnow())
                )
            except Exception as e:
                print("Email error:", e)

        # =============================
        # 📡 Broadcast to Dashboard
        # =============================
        if scam_found:
            await broadcast_dashboard_update({
                "session_id": session_id,
                "message": message_text,
                "upi_ids": upi_matches,
                "phone_numbers": phone_matches,
                "timestamp": datetime.utcnow().isoformat()
            })

        # =============================
        # 🤖 Honeypot Reply
        # =============================
        response = generate_honeypot_response(message_text)
        return response

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return "I'm not sure I understand. Can you explain?"

    finally:
        db.close()


# =====================================================
# 🤖 Honeypot Response Generator
# =====================================================

def generate_honeypot_response(message: str) -> str:
    """Generate realistic honeypot replies"""

    message_lower = message.lower()

    if "bank" in message_lower or "account" in message_lower:
        return "I'm worried about sharing my bank details. Is this really safe?"

    elif "upi" in message_lower or "paytm" in message_lower or "gpay" in message_lower:
        return "I don't have UPI. Can I send money another way?"

    elif "urgent" in message_lower or "immediately" in message_lower:
        return "Why is this so urgent? I need time to think about this."

    elif "otp" in message_lower or "code" in message_lower:
        return "I received a code but I'm not sure if I should share it. What is it for?"

    elif "link" in message_lower or "click" in message_lower:
        return "This link looks suspicious. Are you sure it's safe?"

    elif "money" in message_lower or "transfer" in message_lower or "send" in message_lower:
        return "How much money do I need to send? This seems like a lot."

    elif "verify" in message_lower or "confirm" in message_lower:
        return "What exactly are you trying to verify? I'm confused."

    else:
        return "I'm not sure I understand. Can you explain this again?"
