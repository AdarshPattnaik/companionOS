"""
CoratiaOS Log Manager — System and MAVLink log management.
"""
import os, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel
from commonwealth.api_utils import create_app, run_service


class LogFile(BaseModel):
    name: str
    path: str
    size_bytes: int
    modified: str


app = create_app(title="Log Manager", description="System and MAVLink log management")

LOG_DIRS = ["/var/logs/coratiaos", "/root/.config/coratiaos/logs"]


@app.get("/v1.0/logs")
async def list_logs() -> list[LogFile]:
    """List available log files."""
    logs = []
    for log_dir in LOG_DIRS:
        for filepath in glob.glob(os.path.join(log_dir, "**", "*.log"), recursive=True):
            try:
                stat = os.stat(filepath)
                logs.append(LogFile(
                    name=os.path.basename(filepath),
                    path=filepath,
                    size_bytes=stat.st_size,
                    modified=str(stat.st_mtime),
                ))
            except OSError:
                pass
    return logs


@app.get("/v1.0/logs/{filename}")
async def get_log(filename: str, lines: int = 100) -> dict:
    """Get the last N lines of a log file."""
    for log_dir in LOG_DIRS:
        filepath = os.path.join(log_dir, filename)
        if os.path.exists(filepath):
            with open(filepath) as f:
                all_lines = f.readlines()
            return {"filename": filename, "lines": all_lines[-lines:]}
    return {"error": "Log not found"}


@app.get("/v1.0/logs/{filename}/download")
async def download_log(filename: str):
    """Download a log file."""
    for log_dir in LOG_DIRS:
        filepath = os.path.join(log_dir, filename)
        if os.path.exists(filepath):
            return FileResponse(filepath, filename=filename)
    return {"error": "Log not found"}


@app.delete("/v1.0/logs/{filename}")
async def delete_log(filename: str) -> dict:
    """Delete a log file."""
    for log_dir in LOG_DIRS:
        filepath = os.path.join(log_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"deleted": True}
    return {"deleted": False}


@app.get("/v1.0/journal")
async def get_journal(lines: int = 100) -> dict:
    """Get system journal entries."""
    import subprocess
    try:
        result = subprocess.run(
            ["journalctl", "-n", str(lines), "--no-pager", "-o", "json"],
            capture_output=True, text=True, timeout=10,
        )
        return {"entries": result.stdout.strip().split("\n")}
    except Exception:
        return {"entries": []}


if __name__ == "__main__":
    run_service(app, port=6065, name="Log Manager")
