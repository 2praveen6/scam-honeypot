import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Scam Honeypot API")


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
async def root():
    return {"message": "Scam Honeypot API Running"}


# -----------------------------
# HEALTH CHECK (Railway uses this)
# -----------------------------
@app.get("/health")
async def health():
    return JSONResponse(
        content={
            "status": "healthy"
        },
        status_code=200
    )
