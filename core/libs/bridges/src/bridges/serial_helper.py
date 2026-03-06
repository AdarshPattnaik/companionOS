"""
Serial Helper — Utility for detecting and managing serial ports.
"""
import glob
import platform
from typing import Optional

from loguru import logger

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


class SerialHelper:
    """Utilities for serial port detection and management."""

    @staticmethod
    def available_ports() -> list[dict[str, str]]:
        """List all available serial ports."""
        if not HAS_SERIAL:
            return []
        ports = serial.tools.list_ports.comports()
        return [
            {
                "device": port.device,
                "name": port.name,
                "description": port.description,
                "hwid": port.hwid,
                "vid": f"0x{port.vid:04X}" if port.vid else None,
                "pid": f"0x{port.pid:04X}" if port.pid else None,
                "manufacturer": port.manufacturer,
                "product": port.product,
            }
            for port in ports
        ]

    @staticmethod
    def detect_flight_controller() -> Optional[dict[str, str]]:
        """Auto-detect a connected flight controller."""
        # Common FC USB vendor/product IDs
        FC_IDENTIFIERS = [
            {"vid": 0x2DAE, "name": "Holybro"},      # Pixhawk
            {"vid": 0x1209, "name": "ArduPilot"},     # ChibiOS
            {"vid": 0x26AC, "name": "3DR"},            # 3DR Pixhawk
            {"vid": 0x2341, "name": "Arduino"},         # Arduino-based FC
        ]

        if not HAS_SERIAL:
            return None

        for port in serial.tools.list_ports.comports():
            for fc in FC_IDENTIFIERS:
                if port.vid == fc["vid"]:
                    logger.info(f"Detected flight controller: {fc['name']} on {port.device}")
                    return {
                        "device": port.device,
                        "name": fc["name"],
                        "description": port.description,
                    }

        # Fallback: check common serial paths on Linux
        if platform.system() == "Linux":
            common_paths = ["/dev/ttyACM0", "/dev/ttyAMA0", "/dev/serial0"]
            for path in common_paths:
                if glob.glob(path):
                    return {"device": path, "name": "Unknown FC", "description": "Auto-detected serial"}

        return None
