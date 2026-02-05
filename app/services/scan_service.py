import uuid
from app.services.guvi_service import process_guvi_event


def scan_message_simple(message: str) -> dict:
    """
    Simple public scam scan
    """

    fake_event = {
        "sessionId": f"public-{uuid.uuid4()}",
        "platform": "public",
        "user_id": "anonymous",
        "message": {
            "sender": "user",
            "text": message,
            "timestamp": 0
        },
        "conversationHistory": []
    }

    reply = process_guvi_event(fake_event)

    scam_keywords = [
        "otp",
        "urgent",
        "blocked",
        "verify",
        "send money",
        "upi",
        "bank"
    ]

    is_scam = any(
        word in message.lower()
        for word in scam_keywords
    )

    return {
        "is_scam": is_scam,
        "reply": reply
    }
