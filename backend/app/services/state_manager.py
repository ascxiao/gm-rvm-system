"""State machine service for the vending system."""
import logging
import csv
from datetime import datetime
from pathlib import Path
from app.models import State, SystemState
from app.modules.ai import RealAI
from app.modules.arduino import MockArduino

logger = logging.getLogger(__name__)


class StateManager:
    """Orchestrates system state transitions and core business logic."""

    def __init__(self):
        self.current_state = SystemState(state=State.IDLE)
        self.bottle_id = 0
        self.ai = RealAI()
        self.arduino = MockArduino()

        base_dir = Path(__file__).parent.parent.parent
        self.logs_dir = base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = self.logs_dir / f"bottle_log_{timestamp}.csv"

        self._initialize()
        self._init_csv()

    def _init_csv(self):
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["bottle_id", "timestamp", "detected_class", "confidence"]
            )
        logger.info("CSV log file created at %s", self.csv_file)

    def _log_to_csv(self, detected_class: str, confidence: float):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [self.bottle_id, timestamp, detected_class, confidence]
                )
            self.bottle_id += 1
        except Exception as e:
            logger.error("Failed to write to CSV: %s", e)

    def _initialize(self):
        logger.info("Initializing system")
        self.arduino.connect()
        self.arduino.close_trapdoor()
        logger.info("System ready")

    def get_status(self) -> SystemState:
        return self.current_state

    def start_scan(self) -> SystemState:
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
        if self.current_state.state != State.VALID_ITEM:
            return self.current_state

        self.arduino.close_trapdoor()
        logger.info("Trapdoor closed")

        self.current_state = SystemState(
            state=State.PRINTING,
            item_detected=self.current_state.item_detected,
            confidence=self.current_state.confidence,
        )
        logger.info("State transition: VALID_ITEM -> PRINTING")

        logger.info(
            "Bottle accepted | bottle_id=%d | confidence=%.2f",
            self.bottle_id,
            self.current_state.confidence,
        )

        self._log_to_csv(
            self.current_state.item_detected,
            self.current_state.confidence,
        )

        logger.info("Reward printing triggered (placeholder)")
        
        # Auto-transition to IDLE after brief reward processing
        self.current_state = SystemState(state=State.IDLE)
        logger.info("State transition: PRINTING -> IDLE")

        return self.current_state

    def handle_invalid_removal(self) -> SystemState:
        if self.current_state.state != State.INVALID_ITEM:
            return self.current_state

        self.current_state = SystemState(state=State.IDLE)
        logger.info("State transition: INVALID_ITEM -> IDLE")
        return self.current_state

    def reset(self) -> SystemState:
        self.arduino.close_trapdoor()
        self.current_state = SystemState(state=State.IDLE)
        logger.warning("System reset to IDLE")
        return self.current_state

    def shutdown(self):
        logger.info("Shutting down system")
        self.arduino.close_trapdoor()
        self.arduino.disconnect()
        self.ai.release_camera()
        logger.info("Shutdown complete")