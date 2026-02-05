from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Scam Honeypot API")


# -----------------------------
# HEALTHCHECK (for Railway)
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------
# API KEY
# -----------------------------
SECRET_API_KEY = os.getenv(
    "SECRET_API_KEY",
    "my_secret_hackathon_key_789"
)

api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)

def verify_key(api_key: str = Security(api_key_header)):
    if api_key != SECRET_API_KEY:
        raise HTTPException(401, "Invalid API Key")
    return api_key


# -----------------------------
# HONEYPOT ENDPOINT
# -----------------------------
@app.post("/api/guvi/honeypot")
async def honeypot(
    data: dict,
    api_key: str = Depends(verify_key)
):
    message = data.get("message", {}).get(
        "text",
        "No message"
    )

    # Simple honeypot reply
    if "otp" in message.lower():
        reply = "I received a code but not sure if I should share it."
    elif "money" in message.lower():
        reply = "How much money do you need?"
    else:
        reply = "Can you explain more?"

    return {
        "reply": reply
    }
