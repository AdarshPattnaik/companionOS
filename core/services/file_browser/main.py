"""
CoratiaOS File Browser — Mission file and log browser.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from loguru import logger
from commonwealth.api_utils import create_app, run_service


class FileEntry(BaseModel):
    name: str
    path: str
    is_directory: bool
    size_bytes: int = 0
    modified: str = ""


app = create_app(title="File Browser", description="File management for missions, logs, and data")

BROWSE_ROOT = "/usr/coratiaos/userdata"


@app.get("/v1.0/files")
async def list_files(path: str = "/") -> list[FileEntry]:
    """List files in directory."""
    full_path = os.path.join(BROWSE_ROOT, path.lstrip("/"))
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)

    entries = []
    try:
        for entry in os.scandir(full_path):
            stat = entry.stat()
            entries.append(FileEntry(
                name=entry.name,
                path=os.path.relpath(entry.path, BROWSE_ROOT),
                is_directory=entry.is_dir(),
                size_bytes=stat.st_size if entry.is_file() else 0,
                modified=str(stat.st_mtime),
            ))
    except PermissionError:
        pass
    return sorted(entries, key=lambda e: (not e.is_directory, e.name))


@app.get("/v1.0/files/download")
async def download_file(path: str):
    """Download a file."""
    full_path = os.path.join(BROWSE_ROOT, path.lstrip("/"))
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path, filename=os.path.basename(full_path))
    return {"error": "File not found"}


@app.post("/v1.0/files/upload")
async def upload_file(path: str = "/", file: UploadFile = File(...)) -> dict:
    """Upload a file."""
    full_dir = os.path.join(BROWSE_ROOT, path.lstrip("/"))
    os.makedirs(full_dir, exist_ok=True)
    filepath = os.path.join(full_dir, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"success": True, "path": os.path.relpath(filepath, BROWSE_ROOT)}


@app.post("/v1.0/files/mkdir")
async def create_directory(path: str) -> dict:
    """Create a directory."""
    full_path = os.path.join(BROWSE_ROOT, path.lstrip("/"))
    os.makedirs(full_path, exist_ok=True)
    return {"success": True}


@app.delete("/v1.0/files")
async def delete_file(path: str) -> dict:
    """Delete a file or directory."""
    import shutil
    full_path = os.path.join(BROWSE_ROOT, path.lstrip("/"))
    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return {"deleted": True}
    return {"deleted": False}


if __name__ == "__main__":
    run_service(app, port=7070, name="File Browser")
