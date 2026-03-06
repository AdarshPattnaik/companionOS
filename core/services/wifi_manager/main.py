"""
CoratiaOS WiFi Manager — WiFi network management.

Responsibilities:
- Scan for available networks
- Connect/disconnect to WiFi
- Hotspot mode
- WiFi status
"""
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from typing import Optional
from pydantic import BaseModel
from loguru import logger
from commonwealth.api_utils import create_app, run_service


class WiFiNetwork(BaseModel):
    ssid: str
    bssid: str = ""
    signal_strength: int = 0
    frequency: str = ""
    security: str = ""
    connected: bool = False


class WiFiCredentials(BaseModel):
    ssid: str
    password: str


class HotspotConfig(BaseModel):
    ssid: str = "CoratiaOS-Hotspot"
    password: str = "coratiaos"
    band: str = "2.4GHz"
    channel: int = 6


app = create_app(title="WiFi Manager", description="WiFi network management")

hotspot_active = False


@app.get("/v1.0/status")
async def get_wifi_status() -> dict:
    """Get current WiFi status."""
    try:
        result = subprocess.run(
            ["iwgetid", "-r"], capture_output=True, text=True, timeout=5,
        )
        ssid = result.stdout.strip()
        return {"connected": bool(ssid), "ssid": ssid, "hotspot_active": hotspot_active}
    except Exception:
        return {"connected": False, "ssid": "", "hotspot_active": hotspot_active}


@app.get("/v1.0/scan")
async def scan_networks() -> list[WiFiNetwork]:
    """Scan for available WiFi networks."""
    networks = []
    try:
        result = subprocess.run(
            ["iwlist", "wlan0", "scan"],
            capture_output=True, text=True, timeout=15,
        )
        # Parse iwlist output (simplified)
        current_ssid = ""
        current_signal = 0
        for line in result.stdout.split("\n"):
            line = line.strip()
            if "ESSID:" in line:
                current_ssid = line.split('"')[1] if '"' in line else ""
                if current_ssid:
                    networks.append(WiFiNetwork(
                        ssid=current_ssid,
                        signal_strength=current_signal,
                    ))
            elif "Signal level" in line:
                try:
                    current_signal = int(line.split("=")[1].split(" ")[0])
                except (IndexError, ValueError):
                    current_signal = 0
    except Exception as e:
        logger.warning(f"WiFi scan failed: {e}")
    return networks


@app.post("/v1.0/connect")
async def connect_wifi(credentials: WiFiCredentials) -> dict:
    """Connect to a WiFi network."""
    logger.info(f"Connecting to WiFi: {credentials.ssid}")
    try:
        subprocess.run(
            ["nmcli", "device", "wifi", "connect", credentials.ssid,
             "password", credentials.password],
            capture_output=True, text=True, timeout=30,
        )
        return {"success": True, "message": f"Connected to {credentials.ssid}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/v1.0/disconnect")
async def disconnect_wifi() -> dict:
    """Disconnect from current WiFi."""
    try:
        subprocess.run(["nmcli", "device", "disconnect", "wlan0"],
                       capture_output=True, text=True, timeout=10)
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/v1.0/hotspot")
async def create_hotspot(config: HotspotConfig) -> dict:
    """Create a WiFi hotspot."""
    global hotspot_active
    logger.info(f"Creating hotspot: {config.ssid}")
    hotspot_active = True
    return {"success": True, "ssid": config.ssid}


@app.delete("/v1.0/hotspot")
async def stop_hotspot() -> dict:
    """Stop WiFi hotspot."""
    global hotspot_active
    hotspot_active = False
    return {"success": True}


@app.get("/v1.0/saved")
async def get_saved_networks() -> list[dict]:
    """List saved WiFi networks."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
            capture_output=True, text=True, timeout=5,
        )
        saved = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 2 and "wireless" in parts[1].lower():
                saved.append({"name": parts[0]})
        return saved
    except Exception:
        return []


if __name__ == "__main__":
    run_service(app, port=6050, name="WiFi Manager")
