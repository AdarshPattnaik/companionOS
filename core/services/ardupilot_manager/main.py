"""
CoratiaOS Ardupilot Manager — MAVLink routing and vehicle management.

Responsibilities:
- Flight controller detection
- MAVLink router management
- Endpoint management (UDP/TCP/Serial)
- Parameter read/write
- Telemetry WebSocket streaming
- Firmware management
"""
import asyncio
import json
from enum import Enum
from typing import Any, Optional

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "bridges", "src"))

from commonwealth.api_utils import create_app, run_service
from bridges.serial_helper import SerialHelper


# ── Models ──
class EndpointType(str, Enum):
    UDP_SERVER = "udpserver"
    UDP_CLIENT = "udpclient"
    TCP_SERVER = "tcpserver"
    TCP_CLIENT = "tcpclient"
    SERIAL = "serial"


class Endpoint(BaseModel):
    name: str
    type: EndpointType
    place: str  # e.g., "192.168.2.1:14550" or "/dev/ttyACM0:115200"
    enabled: bool = True
    persistent: bool = True
    protected: bool = False


class VehicleStatus(BaseModel):
    connected: bool = False
    armed: bool = False
    flight_mode: str = "UNKNOWN"
    firmware_type: str = "ArduSub"
    system_id: int = 0
    component_id: int = 0
    battery_voltage: float = 0.0
    battery_remaining: int = 0


# ── Service State ──
class ArdupilotManagerState:
    def __init__(self):
        self.endpoints: list[Endpoint] = [
            Endpoint(
                name="GCS Client",
                type=EndpointType.UDP_CLIENT,
                place="192.168.2.1:14550",
                protected=True,
            ),
            Endpoint(
                name="MAVLink2Rest",
                type=EndpointType.UDP_SERVER,
                place="127.0.0.1:14551",
                protected=True,
            ),
        ]
        self.vehicle_status = VehicleStatus()
        self.serial_helper = SerialHelper()
        self.detected_board: Optional[dict] = None
        self.telemetry_clients: list[WebSocket] = []

    def detect_flight_controller(self) -> Optional[dict]:
        self.detected_board = self.serial_helper.detect_flight_controller()
        if self.detected_board:
            self.vehicle_status.connected = True
            logger.info(f"Flight controller detected: {self.detected_board}")
        return self.detected_board


state = ArdupilotManagerState()

# ── App ──
app = create_app(
    title="Ardupilot Manager",
    description="MAVLink routing, vehicle management, and telemetry",
)


@app.get("/v1.0/vehicle/status")
async def get_vehicle_status() -> VehicleStatus:
    """Get current vehicle status."""
    return state.vehicle_status


@app.get("/v1.0/vehicle/detect")
async def detect_vehicle() -> dict[str, Any]:
    """Detect connected flight controller."""
    board = state.detect_flight_controller()
    return {"detected": board is not None, "board": board}


@app.get("/v1.0/serials")
async def get_serial_ports() -> list[dict]:
    """List available serial ports."""
    return state.serial_helper.available_ports()


# ── Endpoints Management ──
@app.get("/v1.0/endpoints")
async def get_endpoints() -> list[Endpoint]:
    """List all MAVLink endpoints."""
    return state.endpoints


@app.post("/v1.0/endpoints")
async def create_endpoint(endpoint: Endpoint) -> Endpoint:
    """Create a new MAVLink endpoint."""
    state.endpoints.append(endpoint)
    logger.info(f"Endpoint created: {endpoint.name}")
    return endpoint


@app.delete("/v1.0/endpoints/{name}")
async def delete_endpoint(name: str) -> dict:
    """Delete a MAVLink endpoint by name."""
    for i, ep in enumerate(state.endpoints):
        if ep.name == name and not ep.protected:
            state.endpoints.pop(i)
            return {"deleted": True}
    return {"deleted": False, "error": "Endpoint not found or protected"}


@app.put("/v1.0/endpoints/{name}")
async def update_endpoint(name: str, endpoint: Endpoint) -> Endpoint:
    """Update an existing endpoint."""
    for i, ep in enumerate(state.endpoints):
        if ep.name == name:
            state.endpoints[i] = endpoint
            return endpoint
    state.endpoints.append(endpoint)
    return endpoint


# ── Parameters ──
@app.get("/v1.0/parameters")
async def get_parameters() -> dict:
    """Get all vehicle parameters (mock for dev)."""
    return {
        "parameters": {
            "SYSID_THISMAV": {"value": 1, "type": "INT32", "description": "MAVLink system ID"},
            "ARMING_CHECK": {"value": 1, "type": "INT32", "description": "Arming checks to perform"},
            "PILOT_SPEED_DN": {"value": 150, "type": "INT32", "description": "Pilot max descent speed"},
            "PILOT_SPEED_UP": {"value": 150, "type": "INT32", "description": "Pilot max ascent speed"},
        }
    }


# ── Telemetry WebSocket ──
@app.websocket("/v1.0/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket) -> None:
    """Stream vehicle telemetry over WebSocket."""
    await websocket.accept()
    state.telemetry_clients.append(websocket)
    logger.info("Telemetry client connected")
    try:
        while True:
            telemetry = {
                "timestamp": asyncio.get_event_loop().time(),
                "armed": state.vehicle_status.armed,
                "mode": state.vehicle_status.flight_mode,
                "battery_voltage": state.vehicle_status.battery_voltage,
                "battery_remaining": state.vehicle_status.battery_remaining,
                "depth": 0.0,
                "heading": 0,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
            }
            await websocket.send_json(telemetry)
            await asyncio.sleep(0.1)  # 10 Hz
    except WebSocketDisconnect:
        state.telemetry_clients.remove(websocket)
        logger.info("Telemetry client disconnected")


# ── Firmware ──
@app.get("/v1.0/firmware/available")
async def get_available_firmware() -> dict:
    """List available firmware versions."""
    return {
        "firmware": [
            {"name": "ArduSub", "version": "4.1.1", "platform": "Pixhawk1"},
            {"name": "ArduSub", "version": "4.5.0", "platform": "Pixhawk1"},
        ]
    }


if __name__ == "__main__":
    run_service(app, port=8000, name="Ardupilot Manager")
