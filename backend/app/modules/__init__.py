"""Mock thermal printer module."""
from datetime import datetime


class MockPrinter:
    """Mock thermal printer interface."""

    def __init__(self, port: str = "COM4"):
        self.port = port
        self.connected = True

    def connect(self) -> bool:
        """Connect to printer."""
        self.connected = True
        print("[PRINTER] Connected")
        return True

    def disconnect(self) -> bool:
        """Disconnect from printer."""
        self.connected = False
        print("[PRINTER] Disconnected")
        return True

    def print_coupon(self, coupon_code: str) -> bool:
        """Print a coupon."""
        if not self.connected:
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        coupon_text = f"""
================================
    RECYCLING COUPON
================================
Code: {coupon_code}
Date: {timestamp}
Value: $0.05

Thank you for recycling!
================================
"""
        print("[PRINTER] Printing:")
        print(coupon_text)
        return True

    def get_status(self) -> dict:
        """Get printer status."""
        return {
            "connected": self.connected,
            "ready": self.connected,
        }
