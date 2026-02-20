import logging
import time
import serial
import threading
from typing import Optional

logger = logging.getLogger(__name__)


class ArduinoController:
    def __init__(self, port: str = "COM5", baudrate: int = 9600, timeout: float = 1.0):
        if port is None:
            port = self._find_arduino_port()
            if port is None:
                logger.warning("No Arduino found, using COM5 as default")
                port = "COM5"

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connected = False
        self.trapdoor_open = False
        self.ser: serial.Serial | None = None

        self.auto_close_timer: Optional[threading.Timer] = None

    def _find_arduino_port(self) -> str | None:
        """Find Arduino port by checking common descriptions."""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()

            arduino_keywords = ['arduino', 'usb serial', 'ch340', 'ftdi', 'cp210']

            for port in ports:
                desc = port.description.lower()
                if any(keyword in desc for keyword in arduino_keywords):
                    logger.info(f"Found Arduino on {port.device}: {port.description}")
                    return port.device

            return None
        except Exception as e:
            logger.error(f"Error detecting Arduino port: {e}")
            return None

    def connect(self) -> bool:
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )
            time.sleep(2)
            try:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except Exception:
                pass
            self.connected = True
            logger.info("Arduino connected")
            return True
        except serial.SerialException as e:
            self.ser = None
            self.connected = False
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        try:
            if self.auto_close_timer:
                self.auto_close_timer.cancel()
                self.auto_close_timer = None

            if self.ser and self.ser.is_open:
                self.ser.close()
        finally:
            self.ser = None
            self.connected = False
            self.trapdoor_open = False
        logger.info("Arduino disconnected")
        return True

    def _send(self, cmd: bytes) -> bool:
        if not self.connected or not self.ser or not self.ser.is_open:
            logger.warning("Serial not connected")
            return False
        try:
            self.ser.write(cmd)
            self.ser.flush()
            return True
        except (serial.SerialException, serial.SerialTimeoutException) as e:
            logger.error(f"Send failed: {e}")
            return False

    def open_trapdoor(self) -> bool:
        if not self.connected:
            logger.warning("Attempted to open trapdoor while Arduino disconnected")
            return False
        if self._send(b"O"):
            self.trapdoor_open = True
            logger.info("🚪 Trapdoor opened - waiting for item drop")
            return True
        return False

    def close_trapdoor(self) -> bool:
        if not self.connected:
            logger.warning("Attempted to close trapdoor while Arduino disconnected")
            return False
        if self._send(b"C"):
            self.trapdoor_open = False
            logger.info("🚪 Trapdoor closed")
            return True
        return False

    def open_trapdoor_with_timer(self, auto_close_delay: float = 2.0) -> bool:
        """Open trapdoor and schedule auto-close after delay."""
        if not self.open_trapdoor():
            return False

        if self.auto_close_timer:
            self.auto_close_timer.cancel()

        self.auto_close_timer = threading.Timer(auto_close_delay, self.close_trapdoor)
        self.auto_close_timer.start()
        logger.info(f"Auto-close scheduled in {auto_close_delay} seconds")
        return True

    def get_status(self) -> dict:
        return {
            "connected": self.connected,
            "trapdoor_open": self.trapdoor_open,
        }