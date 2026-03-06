"""
CoratiaOS MAVLink Communication — Helper for MAVLink message handling.
Wraps pymavlink for simplified vehicle communication.
"""
import asyncio
import time
from typing import Any, Optional

from loguru import logger

try:
    from pymavlink import mavutil
    HAS_PYMAVLINK = True
except ImportError:
    HAS_PYMAVLINK = False
    logger.warning("pymavlink not available — MAVLink features disabled")


class MAVLinkConnection:
    """Manages a MAVLink connection to a vehicle."""

    def __init__(self, connection_string: str = "udpin:0.0.0.0:14550") -> None:
        self._connection_string = connection_string
        self._connection: Any = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        """Establish MAVLink connection."""
        if not HAS_PYMAVLINK:
            logger.error("pymavlink not installed")
            return False
        try:
            self._connection = mavutil.mavlink_connection(self._connection_string)
            self._connection.wait_heartbeat(timeout=10)
            self._connected = True
            logger.info(
                f"MAVLink connected: system {self._connection.target_system}, "
                f"component {self._connection.target_component}"
            )
            return True
        except Exception as e:
            logger.error(f"MAVLink connection failed: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close the MAVLink connection."""
        if self._connection:
            self._connection.close()
        self._connected = False

    def get_message(self, msg_type: str, timeout: float = 5.0) -> Optional[Any]:
        """Wait for a specific MAVLink message."""
        if not self._connection:
            return None
        try:
            return self._connection.recv_match(type=msg_type, blocking=True, timeout=timeout)
        except Exception as e:
            logger.error(f"Failed to receive {msg_type}: {e}")
            return None

    def send_heartbeat(self) -> None:
        """Send a heartbeat message."""
        if self._connection:
            self._connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0,
            )

    def request_parameter(self, param_id: str) -> Optional[float]:
        """Request a single parameter value."""
        if not self._connection:
            return None
        try:
            self._connection.mav.param_request_read_send(
                self._connection.target_system,
                self._connection.target_component,
                param_id.encode("utf-8"),
                -1,
            )
            msg = self._connection.recv_match(type="PARAM_VALUE", blocking=True, timeout=5)
            return msg.param_value if msg else None
        except Exception as e:
            logger.error(f"Failed to read param {param_id}: {e}")
            return None

    def set_parameter(self, param_id: str, value: float, param_type: int = 0) -> bool:
        """Set a parameter value on the vehicle."""
        if not self._connection:
            return False
        try:
            self._connection.mav.param_set_send(
                self._connection.target_system,
                self._connection.target_component,
                param_id.encode("utf-8"),
                value,
                param_type,
            )
            msg = self._connection.recv_match(type="PARAM_VALUE", blocking=True, timeout=5)
            return msg is not None
        except Exception as e:
            logger.error(f"Failed to set param {param_id}: {e}")
            return False

    def get_vehicle_info(self) -> dict[str, Any]:
        """Get basic vehicle information from heartbeat."""
        if not self._connection:
            return {}
        heartbeat = self.get_message("HEARTBEAT", timeout=3)
        if not heartbeat:
            return {}
        return {
            "type": heartbeat.type,
            "autopilot": heartbeat.autopilot,
            "base_mode": heartbeat.base_mode,
            "custom_mode": heartbeat.custom_mode,
            "system_status": heartbeat.system_status,
            "armed": bool(heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED),
        }
