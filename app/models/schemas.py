from pydantic import BaseModel
from typing import Optional, List

# ============ GUVI API SCHEMAS ============

class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int

class ConversationMessage(BaseModel):
    sender: str
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class HoneypotRequest(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: List[ConversationMessage] = []
    metadata: Optional[Metadata] = None

class HoneypotResponse(BaseModel):
    status: str
    reply: str

# ============ EXTRACTED INTELLIGENCE ============

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

# ============ GUVI CALLBACK SCHEMA ============

class GuviCallbackPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str

# ============ INTERNAL SCHEMAS ============

class SessionState(BaseModel):
    sessionId: str
    conversation_log: List[dict] = []
    extracted_intelligence: ExtractedIntelligence = ExtractedIntelligence()
    turn_count: int = 0
    scam_detected: bool = False
    scam_type: Optional[str] = None
    agent_notes: List[str] = []

# ============ BASIC ANALYSIS SCHEMAS ============

class MessageRequest(BaseModel):
    message: str

class AnalysisResponse(BaseModel):
    is_scam: bool
    confidence: int
    scam_type: Optional[str]
    red_flags: List[str]
    explanation: str
    advice: str