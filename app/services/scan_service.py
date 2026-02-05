def scan_message_simple(message: str):

    text = message.lower()

    red_flags = []

    if "otp" in text:
        red_flags.append("Asking for OTP")

    if "urgent" in text:
        red_flags.append("Creates urgency")

    if "bank" in text:
        red_flags.append("Bank detail request")

    if "upi" in text or "@paytm" in text:
        red_flags.append("UPI payment request")

    is_scam = len(red_flags) > 0

    return {
        "success": True,
        "is_scam": is_scam,
        "confidence": 85 if is_scam else 20,
        "scam_type": "Financial Scam" if is_scam else None,
        "red_flags": red_flags,
        "explanation": "Message shows scam patterns"
        if is_scam else "No major scam indicators detected",
        "advice": "Do not share OTP or money"
        if is_scam else "Stay cautious"
    }
