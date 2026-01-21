"""State machine service for the vending system."""
import uuid
import logging
from app.models import State, SystemState
from app.modules.ai import RealAI
from app.modules.arduino import MockArduino
from app.modules import MockPrinter

logger = logging.getLogger(__name__)


class StateManager:
    """Orchestrates system state transitions and logic."""

    def __init__(self):
        """Initialize system state and modules."""
        self.current_state = SystemState(state=State.IDLE)
        self.ai = RealAI()
        self.arduino = MockArduino()
        self.printer = MockPrinter()
        self._initialize()

    def _initialize(self):
        """Initialize hardware and prepare system."""
        logger.info("Initializing system")
        self.arduino.connect()
        self.arduino.close_trapdoor()
        self.printer.connect()
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

        coupon_code = f"COUPON-{uuid.uuid4().hex[:8].upper()}"

        self.arduino.close_trapdoor()
        logger.info("Trapdoor closed")

        self.current_state = SystemState(
            state=State.PRINTING,
            item_detected=self.current_state.item_detected,
            confidence=self.current_state.confidence,
            coupon_code=coupon_code,
        )
        logger.info("State transition: VALID_ITEM -> PRINTING")

        self.printer.print_coupon(coupon_code)

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
        self.printer.disconnect()
        logger.info("Shutdown complete")