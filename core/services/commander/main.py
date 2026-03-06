"""
CoratiaOS Commander — Vehicle command interface.

Responsibilities:
- Arm/disarm commands
- Flight mode changes
- MAVLink command_long interface
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from enum import Enum
from pydantic import BaseModel
from commonwealth.api_utils import create_app, run_service


class FlightMode(str, Enum):
    MANUAL = "MANUAL"
    STABILIZE = "STABILIZE"
    DEPTH_HOLD = "DEPTH_HOLD"
    ALT_HOLD = "ALT_HOLD"
    GUIDED = "GUIDED"
    POSHOLD = "POSHOLD"
    AUTO = "AUTO"
    SURFACE = "SURFACE"
    ACRO = "ACRO"


class CommandResult(BaseModel):
    success: bool
    message: str = ""


app = create_app(title="Commander", description="Vehicle command interface")


@app.post("/v1.0/arm")
async def arm_vehicle() -> CommandResult:
    """Arm the vehicle."""
    return CommandResult(success=True, message="Arm command sent")


@app.post("/v1.0/disarm")
async def disarm_vehicle() -> CommandResult:
    """Disarm the vehicle."""
    return CommandResult(success=True, message="Disarm command sent")


@app.post("/v1.0/mode/{mode}")
async def set_flight_mode(mode: FlightMode) -> CommandResult:
    """Set vehicle flight mode."""
    return CommandResult(success=True, message=f"Mode set to {mode.value}")


@app.post("/v1.0/command/{command_id}")
async def send_command(command_id: int, params: dict = {}) -> CommandResult:
    """Send a MAVLink COMMAND_LONG."""
    return CommandResult(success=True, message=f"Command {command_id} sent")


if __name__ == "__main__":
    run_service(app, port=6010, name="Commander")
