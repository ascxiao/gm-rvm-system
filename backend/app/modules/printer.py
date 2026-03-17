import logging
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)

def print_receipt(
    text: str,
    printer_name: str = "YiDa_YD583",
    wait_for_trapdoor: Optional[callable] = None,
    retries: int = 2,
):
    """
    Print receipt using ESC/POS commands via CUPS for YiDa YD583 thermal printer.

    Args:
        text (str): The receipt text to print.
        printer_name (str): The CUPS printer name.
        wait_for_trapdoor (callable, optional): Function returning True when trapdoor is closed.
        retries (int): Number of print attempts if it fails.
    """
    if wait_for_trapdoor:
        logger.info("Waiting for Arduino trapdoor to close before printing...")
        while not wait_for_trapdoor():
            time.sleep(0.1)
        logger.info("Trapdoor is closed. Proceeding to print.")

    # ESC/POS commands
    ESC = b'\x1b'
    GS = b'\x1d'
    CUT_FULL = GS + b'V' + b'\x00'  # Full cut
    FEED_LINES = b'\n' * 3          # feed 3 lines at end

    # Convert text to bytes with trailing line feeds
    receipt_bytes = text.encode("utf-8") + FEED_LINES + CUT_FULL

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Printing to '{printer_name}' via CUPS raw mode (Attempt {attempt})...")
            subprocess.run(
                ["lp", "-d", printer_name, "-o", "raw"],
                input=receipt_bytes,
                check=True
            )
            logger.info(f"📠 Receipt sent to printer '{printer_name}' successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Attempt {attempt}: Failed to print via CUPS: {e}")
        time.sleep(0.5)

    logger.error(f"No printer detected or print failed after {retries} attempts")
    return False