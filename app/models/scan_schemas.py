from pydantic import BaseModel


class ScanRequest(BaseModel):
    message: str


class ScanResponse(BaseModel):
    is_scam: bool
    reply: str
