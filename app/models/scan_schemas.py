from pydantic import BaseModel


class ScanRequest(BaseModel):
    message: str


class ScanResponse(BaseModel):
    success: bool
    is_scam: bool
    confidence: int
    scam_type: str | None
    red_flags: list[str]
    explanation: str
    advice: str
