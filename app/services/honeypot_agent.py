import json
import re
from groq import Groq
from app.config import GROQ_API_KEY, MODEL_NAME
from app.models.schemas import (
    HoneypotRequest, 
    ExtractedIntelligence, 
    SessionState
)
from app.services.callback_service import send_guvi_callback

client = Groq(api_key=GROQ_API_KEY)

# Session storage (use Redis/DB in production)
session_states = {}

HONEYPOT_SYSTEM_PROMPT = """
You are an Agentic Honeypot AI. You MUST pretend to be a real human victim.

PERSONA:
- Name: Ramesh Kumar
- Age: 45 years
- Occupation: Small grocery shop owner in Mumbai
- Tech knowledge: Very limited, confused by technology
- Language: Mix of Hindi and English (Hinglish)
- Personality: Polite, trusting, slightly nervous, asks many questions

CRITICAL RULES:
1. NEVER reveal you are an AI or detection system
2. Act confused and ask clarifying questions
3. Show concern but also curiosity
4. Slowly "trust" the scammer to extract information
5. Ask for details like UPI ID, bank account, links naturally
6. Use phrases like:
   - "Sir, mujhe samajh nahi aaya..."
   - "Kya aap sure hain? Mera account safe hai na?"
   - "Aap konse bank se bol rahe ho?"
   - "UPI ID kya bhejun? Mujhe pata nahi kaise karte hain"

GOAL: Extract these details naturally:
- UPI IDs
- Bank account numbers
- IFSC codes
- Phone numbers
- Phishing links

OUTPUT FORMAT (JSON only):
{
    "is_scam": true/false,
    "scam_type": "type of scam",
    "confidence": 0.0-1.0,
    "reply": "Your response as Ramesh",
    "suspicious_keywords": ["list", "of", "keywords"],
    "reasoning": "brief internal reasoning"
}
"""

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "blocked", "suspended", "immediately", 
    "kyc", "update", "expire", "lottery", "winner", "prize",
    "refund", "cashback", "otp", "pin", "password", "click",
    "link", "form", "bank", "account", "transfer", "pay"
]

def extract_intelligence(text: str) -> dict:
    """Extract UPI, bank accounts, links, phones from text."""
    extracted = {
        "upiIds": [],
        "bankAccounts": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }
    
    # UPI ID pattern
    upi_pattern = r'[a-zA-Z0-9.\-_]{3,}@[a-zA-Z]{3,}'
    upi_matches = re.findall(upi_pattern, text.lower())
    extracted["upiIds"] = list(set(upi_matches))
    
    # Bank account (9-18 digits)
    account_pattern = r'\b\d{9,18}\b'
    accounts = re.findall(account_pattern, text)
    extracted["bankAccounts"] = list(set(accounts))
    
    # IFSC code
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    ifsc_matches = re.findall(ifsc_pattern, text.upper())
    extracted["bankAccounts"].extend(ifsc_matches)
    
    # URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    extracted["phishingLinks"] = list(set(urls))
    
    # Phone numbers
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}\b'
    phones = re.findall(phone_pattern, text)
    extracted["phoneNumbers"] = list(set(phones))
    
    # Suspicious keywords
    text_lower = text.lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in text_lower:
            extracted["suspiciousKeywords"].append(keyword)
    
    return extracted

def merge_intelligence(existing: ExtractedIntelligence, new: dict) -> ExtractedIntelligence:
    """Merge new intelligence with existing."""
    return ExtractedIntelligence(
        bankAccounts=list(set(existing.bankAccounts + new.get("bankAccounts", []))),
        upiIds=list(set(existing.upiIds + new.get("upiIds", []))),
        phishingLinks=list(set(existing.phishingLinks + new.get("phishingLinks", []))),
        phoneNumbers=list(set(existing.phoneNumbers + new.get("phoneNumbers", []))),
        suspiciousKeywords=list(set(existing.suspiciousKeywords + new.get("suspiciousKeywords", [])))
    )

def get_or_create_session(session_id: str) -> SessionState:
    """Get existing session or create new one."""
    if session_id not in session_states:
        session_states[session_id] = SessionState(sessionId=session_id)
    return session_states[session_id]

def build_conversation_context(request: HoneypotRequest, state: SessionState) -> str:
    """Build context from conversation history."""
    context_parts = []
    
    # Add conversation history
    for msg in request.conversationHistory:
        role = "SCAMMER" if msg.sender == "scammer" else "RAMESH"
        context_parts.append(f"{role}: {msg.text}")
    
    # Add current message
    context_parts.append(f"SCAMMER: {request.message.text}")
    
    return "\n".join(context_parts)

def process_honeypot_request(request: HoneypotRequest) -> dict:
    """Main honeypot processing function."""
    
    # Get or create session
    state = get_or_create_session(request.sessionId)
    state.turn_count += 1
    
    # Extract intelligence from current message
    new_intel = extract_intelligence(request.message.text)
    
    # Also extract from conversation history
    for msg in request.conversationHistory:
        if msg.sender == "scammer":
            hist_intel = extract_intelligence(msg.text)
            new_intel["upiIds"].extend(hist_intel["upiIds"])
            new_intel["bankAccounts"].extend(hist_intel["bankAccounts"])
            new_intel["phishingLinks"].extend(hist_intel["phishingLinks"])
            new_intel["phoneNumbers"].extend(hist_intel["phoneNumbers"])
            new_intel["suspiciousKeywords"].extend(hist_intel["suspiciousKeywords"])
    
    # Merge with existing intelligence
    state.extracted_intelligence = merge_intelligence(state.extracted_intelligence, new_intel)
    
    # Build conversation context
    conversation_context = build_conversation_context(request, state)
    
    # Build prompt for AI
    intel_summary = json.dumps({
        "upiIds": state.extracted_intelligence.upiIds,
        "bankAccounts": state.extracted_intelligence.bankAccounts,
        "phishingLinks": state.extracted_intelligence.phishingLinks,
        "phoneNumbers": state.extracted_intelligence.phoneNumbers
    }, indent=2)
    
    prompt = f"""
CONVERSATION SO FAR:
{conversation_context}

INTELLIGENCE ALREADY COLLECTED:
{intel_summary}

METADATA:
- Channel: {request.metadata.channel if request.metadata else 'SMS'}
- Language: {request.metadata.language if request.metadata else 'English'}
- Turn: {state.turn_count}

TASK: 
1. Determine if this is a scam
2. Generate a response as Ramesh to continue the conversation
3. Try to extract more information naturally
4. Do NOT ask for information already collected

Respond with JSON only.
"""
    
    # Call AI
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": HONEYPOT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            ai_result = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")
            
    except Exception as e:
        # Fallback response
        ai_result = {
            "is_scam": True,
            "scam_type": "unknown",
            "confidence": 0.7,
            "reply": "Sir, mujhe samajh nahi aaya. Thoda detail mein bataiye?",
            "suspicious_keywords": [],
            "reasoning": "Fallback response due to error"
        }
    
    # Update state
    state.scam_detected = ai_result.get("is_scam", True)
    state.scam_type = ai_result.get("scam_type", "unknown")
    
    if ai_result.get("reasoning"):
        state.agent_notes.append(ai_result["reasoning"])
    
    # Add suspicious keywords from AI
    if ai_result.get("suspicious_keywords"):
        state.extracted_intelligence.suspiciousKeywords = list(set(
            state.extracted_intelligence.suspiciousKeywords + 
            ai_result.get("suspicious_keywords", [])
        ))
    
    # Check if we should send callback (after sufficient engagement)
    intel = state.extracted_intelligence
    has_intel = (
        len(intel.upiIds) > 0 or 
        len(intel.bankAccounts) > 0 or 
        len(intel.phishingLinks) > 0 or
        len(intel.phoneNumbers) > 0
    )
    
    # Send callback if scam detected and we have intelligence or enough turns
    if state.scam_detected and (has_intel or state.turn_count >= 3):
        # Calculate total messages (history + current exchanges)
        total_messages = len(request.conversationHistory) + 2  # +2 for current exchange
        
        # Generate agent notes
        agent_notes = f"Scam type: {state.scam_type}. " + " ".join(state.agent_notes[-3:])
        
        # Send callback asynchronously (don't block response)
        try:
            send_guvi_callback(
                session_id=request.sessionId,
                scam_detected=state.scam_detected,
                total_messages=total_messages,
                intelligence=state.extracted_intelligence,
                agent_notes=agent_notes
            )
        except Exception as e:
            print(f"Callback error: {e}")
    
    # Save updated state
    session_states[request.sessionId] = state
    
    # Return response in GUVI format
    return {
        "status": "success",
        "reply": ai_result.get("reply", "Sir, mujhe samajh nahi aaya.")
    }

def get_session_state(session_id: str) -> dict:
    """Get current session state for debugging."""
    if session_id in session_states:
        state = session_states[session_id]
        return {
            "sessionId": state.sessionId,
            "turnCount": state.turn_count,
            "scamDetected": state.scam_detected,
            "scamType": state.scam_type,
            "extractedIntelligence": state.extracted_intelligence.dict()
        }
    return {"error": "Session not found"}

def reset_session(session_id: str) -> dict:
    """Reset a session."""
    if session_id in session_states:
        del session_states[session_id]
        return {"status": "reset", "sessionId": session_id}
    return {"status": "not_found", "sessionId": session_id}