"""State definitions for the reverse vending machine."""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class State(str, Enum):
    """System states."""
    IDLE = "idle"
    SCANNING = "scanning"
    VALID_ITEM = "valid_item"
    INVALID_ITEM = "invalid_item"
    PRINTING = "printing"


@dataclass
class SystemState:
    """Represents the current system state."""
    state: State
    item_detected: Optional[str] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None
    coupon_code: Optional[str] = None

    def to_dict(self):
        return {
            "state": self.state.value,
            "item_detected": self.item_detected,
            "confidence": self.confidence,
            "error_message": self.error_message,
            "coupon_code": self.coupon_code,
        }
