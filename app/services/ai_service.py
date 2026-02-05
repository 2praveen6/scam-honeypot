from groq import Groq
from app.config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a scam detection expert. Analyze messages for scam indicators.

Look for these red flags:
- Urgent language ("act now", "immediately", "limited time")
- Requests for money, gift cards, or cryptocurrency
- Requests for personal info (SSN, passwords, bank details)
- Too-good-to-be-true offers
- Impersonation of officials, companies, or family members
- Suspicious links or attachments
- Poor grammar/spelling (common in scam messages)
- Threats or fear tactics
- Unsolicited contact about prizes or inheritance

Respond in this JSON format only:
{
    "is_scam": true/false,
    "confidence": 0-100,
    "scam_type": "type of scam or null",
    "red_flags": ["list", "of", "red flags found"],
    "explanation": "brief explanation",
    "advice": "what the user should do"
}"""

def analyze_message(message: str) -> dict:
    """Analyze a message for scam indicators."""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this message:\n\n{message}"}
        ],
        temperature=0.1
    )
    
    return response.choices[0].message.content