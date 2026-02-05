from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class GuviRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message]

class GuviResponse(BaseModel):
    reply: str