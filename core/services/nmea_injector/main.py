"""
CoratiaOS NMEA Injector — NMEA data injection service.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from pydantic import BaseModel
from commonwealth.api_utils import create_app, run_service


class NMEASocket(BaseModel):
    name: str
    address: str
    port: int
    protocol: str = "udp"  # udp or tcp
    enabled: bool = True


app = create_app(title="NMEA Injector", description="NMEA data injection for GPS and sensors")

sockets: list[NMEASocket] = []


@app.get("/v1.0/sockets")
async def list_sockets() -> list[NMEASocket]:
    return sockets


@app.post("/v1.0/sockets")
async def create_socket(socket: NMEASocket) -> NMEASocket:
    sockets.append(socket)
    return socket


@app.delete("/v1.0/sockets/{name}")
async def delete_socket(name: str) -> dict:
    global sockets
    sockets = [s for s in sockets if s.name != name]
    return {"deleted": True}


if __name__ == "__main__":
    run_service(app, port=6030, name="NMEA Injector")
