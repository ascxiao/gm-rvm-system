"""Mock Arduino trapdoor controller."""
import logging

logger = logging.getLogger(__name__)


class MockArduino:
    """Mock serial interface to Arduino trapdoor."""

    def __init__(self, port: str = "COM3", baudrate: int = 9600):
        """Initialize mock Arduino connection."""
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        self.trapdoor_open = False

    def connect(self) -> bool:
        """Connect to Arduino."""
        self.connected = True
        logger.info("Arduino connected")
        return True

    def disconnect(self) -> bool:
        """Disconnect from Arduino."""
        self.connected = False
        self.trapdoor_open = False
        logger.info("Arduino disconnected")
        return True

    def open_trapdoor(self) -> bool:
        """Open the trapdoor."""
        if not self.connected:
            logger.warning("Attempted to open trapdoor while Arduino disconnected")
            return False

        self.trapdoor_open = True
        logger.info("Trapdoor opened")
        return True

    def close_trapdoor(self) -> bool:
        """Close the trapdoor."""
        if not self.connected:
            logger.warning("Attempted to close trapdoor while Arduino disconnected")
            return False

        self.trapdoor_open = False
        logger.info("Trapdoor closed")
        return True

    def get_status(self) -> dict:
        """Return current Arduino and trapdoor status."""
        return {
            "connected": self.connected,
            "trapdoor_open": self.trapdoor_open,
        }