"""State machine service for the vending system."""
import logging
from datetime import datetime
from app.models import State, SystemState
from app.modules.ai import RealAI
from app.modules.arduino import MockArduino

logger = logging.getLogger(__name__)


class StateManager:
    """Orchestrates system state transitions and core business logic."""

    def __init__(self):
        self.current_state = SystemState(state=State.IDLE)
        self.bottle_count = 0
        self.ai = RealAI()
        self.arduino = MockArduino()
        self._initialize()

    def _initialize(self):
        """Initialize hardware and prepare system."""
        logger.info("Initializing system")
        self.arduino.connect()
        self.arduino.close_trapdoor()
        logger.info("System ready")

    def get_status(self) -> SystemState:
        """Return the current system state."""
        return self.current_state

    def start_scan(self) -> SystemState:
        """IDLE -> SCANNING -> VALID_ITEM | INVALID_ITEM."""
        if self.current_state.state != State.IDLE:
            return self.current_state

        self.current_state = SystemState(state=State.SCANNING)
        logger.info("State transition: IDLE -> SCANNING")

        detected_class, confidence = self.ai.detect(0)
        is_bottle = self.ai.is_water_bottle(detected_class, confidence)

        if is_bottle:
            self.current_state = SystemState(
                state=State.VALID_ITEM,
                item_detected=detected_class,
                confidence=confidence,
            )
            logger.info("State transition: SCANNING -> VALID_ITEM")
            self.arduino.open_trapdoor()
        else:
            self.current_state = SystemState(
                state=State.INVALID_ITEM,
                item_detected=detected_class,
                confidence=confidence,
                error_message="Invalid item. Please remove and try again.",
            )
            logger.info("State transition: SCANNING -> INVALID_ITEM")

        return self.current_state

    def confirm_drop(self) -> SystemState:
        """VALID_ITEM -> PRINTING -> IDLE."""
        if self.current_state.state != State.VALID_ITEM:
            return self.current_state

        self.arduino.close_trapdoor()
        logger.info("Trapdoor closed")

        # Transition to PRINTING
        self.current_state = SystemState(
            state=State.PRINTING,
            item_detected=self.current_state.item_detected,
            confidence=self.current_state.confidence,
        )
        logger.info("State transition: VALID_ITEM -> PRINTING")

        # Log accepted bottle
        self.bottle_count += 1
        timestamp = datetime.now().isoformat(timespec="seconds")

        logger.info(
            "Bottle accepted | count=%d | time=%s | confidence=%.2f",
            self.bottle_count,
            timestamp,
            self.current_state.confidence,
        )

        # Placeholder for future thermal printer integration
        logger.info("Reward printing triggered (placeholder)")

        # Return to IDLE
        self.current_state = SystemState(state=State.IDLE)
        logger.info("State transition: PRINTING -> IDLE")

        return self.current_state

    def handle_invalid_removal(self) -> SystemState:
        """INVALID_ITEM -> IDLE."""
        if self.current_state.state != State.INVALID_ITEM:
            return self.current_state

        self.current_state = SystemState(state=State.IDLE)
        logger.info("State transition: INVALID_ITEM -> IDLE")
        return self.current_state

    def reset(self) -> SystemState:
        """Force system reset to IDLE."""
        self.arduino.close_trapdoor()
        self.current_state = SystemState(state=State.IDLE)
        logger.warning("System reset to IDLE")
        return self.current_state

    def shutdown(self):
        """Gracefully shut down system and hardware."""
        logger.info("Shutting down system")
        self.arduino.close_trapdoor()
        self.arduino.disconnect()
        logger.info("Shutdown complete")