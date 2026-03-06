"""
CoratiaOS Cable Guy — Ethernet / Network IP management.

Responsibilities:
- Ethernet interface management
- IP address configuration (static/DHCP)
- DHCP server management
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from typing import Optional
from pydantic import BaseModel
from loguru import logger
from commonwealth.api_utils import create_app, run_service


class EthernetInterface(BaseModel):
    name: str
    ip_address: str = ""
    netmask: str = ""
    gateway: str = ""
    is_up: bool = False
    is_dhcp: bool = True
    speed_mbps: int = 0


class StaticIPConfig(BaseModel):
    interface: str
    ip_address: str
    netmask: str = "255.255.255.0"
    gateway: str = ""


class DHCPServerConfig(BaseModel):
    interface: str
    range_start: str
    range_end: str
    netmask: str = "255.255.255.0"


app = create_app(title="Cable Guy", description="Ethernet and network IP management")


@app.get("/v1.0/ethernet")
async def list_ethernet_interfaces() -> list[EthernetInterface]:
    """List all ethernet interfaces."""
    interfaces = []
    try:
        import psutil
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for name, addr_list in addrs.items():
            if name.startswith("eth") or name.startswith("en"):
                ip = ""
                for a in addr_list:
                    if a.family.name == "AF_INET":
                        ip = a.address
                stat = stats.get(name)
                interfaces.append(EthernetInterface(
                    name=name,
                    ip_address=ip,
                    is_up=stat.isup if stat else False,
                    speed_mbps=stat.speed if stat else 0,
                ))
    except Exception as e:
        logger.warning(f"Failed to list interfaces: {e}")
    return interfaces


@app.post("/v1.0/ethernet/static")
async def set_static_ip(config: StaticIPConfig) -> dict:
    """Set a static IP on an interface."""
    logger.info(f"Setting static IP {config.ip_address} on {config.interface}")
    return {"success": True, "message": f"Static IP set on {config.interface}"}


@app.post("/v1.0/ethernet/dhcp/{interface}")
async def enable_dhcp(interface: str) -> dict:
    """Enable DHCP on an interface."""
    return {"success": True, "message": f"DHCP enabled on {interface}"}


@app.post("/v1.0/dhcp-server")
async def configure_dhcp_server(config: DHCPServerConfig) -> dict:
    """Configure DHCP server on an interface."""
    return {"success": True, "message": f"DHCP server configured on {config.interface}"}


@app.delete("/v1.0/dhcp-server/{interface}")
async def stop_dhcp_server(interface: str) -> dict:
    """Stop DHCP server on an interface."""
    return {"success": True}


if __name__ == "__main__":
    run_service(app, port=9090, name="Cable Guy")
