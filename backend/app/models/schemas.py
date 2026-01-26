"""Request and response schemas for API endpoints."""
from pydantic import BaseModel
from typing import Optional


class StatusResponse(BaseModel):
    state: str
    item_detected: Optional[str] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None


class ScanResponse(BaseModel):
    success: bool
    state: str
    item_detected: Optional[str] = None
    confidence: Optional[float] = None
    message: str


class ConfirmResponse(BaseModel):
    success: bool
    state: str
    message: str