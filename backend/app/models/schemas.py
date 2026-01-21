"""Request and response schemas for API endpoints."""
from pydantic import BaseModel
from typing import Optional


class StatusResponse(BaseModel):
    """Response with current system status."""
    state: str
    item_detected: Optional[str] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None
    coupon_code: Optional[str] = None


class ScanResponse(BaseModel):
    """Response after scanning an item."""
    success: bool
    state: str
    item_detected: Optional[str] = None
    confidence: Optional[float] = None
    message: str


class ConfirmResponse(BaseModel):
    """Response after confirming drop."""
    success: bool
    state: str
    coupon_code: Optional[str] = None
    message: str
