"""
CoratiaOS System Helper — System monitoring and control.

Responsibilities:
- CPU, RAM, disk, temperature monitoring
- Process listing
- Network interface info
- Power control (reboot/shutdown)
- System diagnostics
"""
import asyncio
import os
import platform
import subprocess
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))
from commonwealth.api_utils import create_app, run_service

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# ── Models ──
class SystemInfo(BaseModel):
    hostname: str = ""
    platform: str = ""
    architecture: str = ""
    kernel: str = ""
    uptime: float = 0
    coratiaos_version: str = "1.0.0"


class CpuInfo(BaseModel):
    usage_percent: float = 0
    frequency_mhz: float = 0
    core_count: int = 0
    temperature: float = 0


class MemoryInfo(BaseModel):
    total_mb: float = 0
    used_mb: float = 0
    available_mb: float = 0
    usage_percent: float = 0


class DiskInfo(BaseModel):
    total_gb: float = 0
    used_gb: float = 0
    free_gb: float = 0
    usage_percent: float = 0


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    status: str


# ── App ──
app = create_app(
    title="System Helper",
    description="System monitoring, diagnostics, and power control",
)


def get_cpu_temperature() -> float:
    """Get CPU temperature (Raspberry Pi)."""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True, text=True, timeout=5,
        )
        return float(result.stdout.replace("temp=", "").replace("'C\n", ""))
    except Exception:
        if HAS_PSUTIL and hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
    return 0.0


@app.get("/v1.0/system/info")
async def get_system_info() -> SystemInfo:
    """Get system information."""
    import time
    boot_time = psutil.boot_time() if HAS_PSUTIL else 0
    return SystemInfo(
        hostname=platform.node(),
        platform=platform.system(),
        architecture=platform.machine(),
        kernel=platform.release(),
        uptime=time.time() - boot_time if boot_time else 0,
    )


@app.get("/v1.0/system/cpu")
async def get_cpu_info() -> CpuInfo:
    """Get CPU information and usage."""
    if not HAS_PSUTIL:
        return CpuInfo()
    freq = psutil.cpu_freq()
    return CpuInfo(
        usage_percent=psutil.cpu_percent(interval=0.5),
        frequency_mhz=freq.current if freq else 0,
        core_count=psutil.cpu_count(),
        temperature=get_cpu_temperature(),
    )


@app.get("/v1.0/system/memory")
async def get_memory_info() -> MemoryInfo:
    """Get memory usage."""
    if not HAS_PSUTIL:
        return MemoryInfo()
    mem = psutil.virtual_memory()
    return MemoryInfo(
        total_mb=mem.total / (1024 * 1024),
        used_mb=mem.used / (1024 * 1024),
        available_mb=mem.available / (1024 * 1024),
        usage_percent=mem.percent,
    )


@app.get("/v1.0/system/disk")
async def get_disk_info() -> DiskInfo:
    """Get disk usage."""
    if not HAS_PSUTIL:
        return DiskInfo()
    disk = psutil.disk_usage("/")
    return DiskInfo(
        total_gb=disk.total / (1024 ** 3),
        used_gb=disk.used / (1024 ** 3),
        free_gb=disk.free / (1024 ** 3),
        usage_percent=disk.percent,
    )


@app.get("/v1.0/system/processes")
async def get_processes() -> list[ProcessInfo]:
    """List running processes."""
    if not HAS_PSUTIL:
        return []
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
        try:
            info = proc.info
            processes.append(ProcessInfo(
                pid=info["pid"],
                name=info["name"],
                cpu_percent=info["cpu_percent"] or 0,
                memory_mb=(info["memory_info"].rss if info["memory_info"] else 0) / (1024 * 1024),
                status=info["status"],
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:50]


@app.get("/v1.0/system/network")
async def get_network_info() -> dict[str, Any]:
    """Get network interface information."""
    if not HAS_PSUTIL:
        return {}
    interfaces = {}
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for name, addr_list in addrs.items():
        interfaces[name] = {
            "addresses": [{"family": str(a.family), "address": a.address} for a in addr_list],
            "is_up": stats.get(name, None).isup if name in stats else False,
            "speed": stats.get(name, None).speed if name in stats else 0,
        }
    return interfaces


# ── WebSocket: Live system stats ──
@app.websocket("/v1.0/ws/system")
async def system_stats_ws(websocket: WebSocket) -> None:
    """Stream live system stats over WebSocket."""
    await websocket.accept()
    try:
        while True:
            if HAS_PSUTIL:
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                data = {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": mem.percent,
                    "disk_percent": disk.percent,
                    "temperature": get_cpu_temperature(),
                    "net_io": {
                        k: {"bytes_sent": v.bytes_sent, "bytes_recv": v.bytes_recv}
                        for k, v in psutil.net_io_counters(pernic=True).items()
                    },
                }
            else:
                data = {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0, "temperature": 0}
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


# ── Power Control ──
@app.post("/v1.0/system/reboot")
async def reboot_system() -> dict:
    """Reboot the system."""
    logger.warning("System reboot requested!")
    subprocess.Popen(["sudo", "reboot"], stdout=subprocess.DEVNULL)
    return {"status": "rebooting"}


@app.post("/v1.0/system/shutdown")
async def shutdown_system() -> dict:
    """Shutdown the system."""
    logger.warning("System shutdown requested!")
    subprocess.Popen(["sudo", "shutdown", "-h", "now"], stdout=subprocess.DEVNULL)
    return {"status": "shutting_down"}


if __name__ == "__main__":
    run_service(app, port=6040, name="System Helper")
