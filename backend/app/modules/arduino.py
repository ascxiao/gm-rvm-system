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
        self.coupon_printed = False

    def connect(self) -> bool:
        """Connect to Arduino."""
        self.connected = True
        logger.info("Arduino connected")
        return True

    def disconnect(self) -> bool:
        """Disconnect from Arduino."""
        self.connected = False
        self.trapdoor_open = False
        self.coupon_printed = False
        logger.info("Arduino disconnected")
        return True

    def open_trapdoor(self) -> bool:
        """Open the trapdoor."""
        if not self.connected:
            logger.warning("Attempted to open trapdoor while Arduino disconnected")
            return False

        self.trapdoor_open = True
        logger.info("🚪 Trapdoor opened - waiting for item drop")
        return True

    def close_trapdoor(self) -> bool:
        """Close the trapdoor."""
        if not self.connected:
            logger.warning("Attempted to close trapdoor while Arduino disconnected")
            return False

        self.trapdoor_open = False
        logger.info("🚪 Trapdoor closed")
        return True

    def print_coupon(self) -> bool:
        """Trigger coupon printing."""
        if not self.connected:
            logger.warning("Attempted to print coupon while Arduino disconnected")
            return False

        self.coupon_printed = True
        logger.info("🎟️  Coupon print signal sent")
        return True

    def reset_coupon_status(self) -> bool:
        """Reset coupon printed status."""
        self.coupon_printed = False
        logger.info("Coupon status reset")
        return True

    def get_status(self) -> dict:
        """Return current Arduino and trapdoor status."""
        return {
            "connected": self.connected,
            "trapdoor_open": self.trapdoor_open,
            "coupon_printed": self.coupon_printed,
        }