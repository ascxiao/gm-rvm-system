"""State definitions for the reverse vending machine."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class State(str, Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    VALID_ITEM = "valid_item"
    INVALID_ITEM = "invalid_item"
    PRINTING = "printing"


@dataclass
class SystemState:
    state: State
    item_detected: Optional[str] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None

    def to_dict(self):
        return {
            "state": self.state.value,
            "item_detected": self.item_detected,
            "confidence": self.confidence,
            "error_message": self.error_message,
        }