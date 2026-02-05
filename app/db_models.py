from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime
from datetime import datetime
from app.db import Base

class HoneypotSession(Base):
    __tablename__ = "honeypot_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    scam_detected = Column(Boolean, default=False)
    total_messages = Column(Integer, default=0)
    
    # Extracted Intelligence
    bank_accounts = Column(Text, default="[]")  # JSON array
    upi_ids = Column(Text, default="[]")  # JSON array
    phone_numbers = Column(Text, default="[]")  # JSON array
    phishing_links = Column(Text, default="[]")  # JSON array
    suspicious_keywords = Column(Text, default="[]")  # JSON array
    
    # Metadata
    scammer_ip = Column(String, nullable=True)
    agent_notes = Column(Text, default="")
    callback_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)