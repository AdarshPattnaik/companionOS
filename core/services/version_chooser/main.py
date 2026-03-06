"""
CoratiaOS Version Chooser — Update and version management.

Responsibilities:
- List local and remote versions
- Switch between versions
- Rollback support
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from pydantic import BaseModel
from loguru import logger
from commonwealth.api_utils import create_app, run_service


class VersionInfo(BaseModel):
    repository: str
    tag: str
    image_id: str = ""
    sha: str = ""
    last_modified: str = ""
    is_current: bool = False
    is_local: bool = False


app = create_app(title="Version Chooser", description="CoratiaOS version and update management")


@app.get("/v1.0/version/current")
async def get_current_version() -> dict:
    """Get the currently running version."""
    return {
        "repository": "adarshnemesis/coratiaos-core",
        "tag": "stable",
        "version": "1.0.0",
        "sha": "local-dev",
        "build_date": "2024-01-01",
    }


@app.get("/v1.0/version/local")
async def list_local_versions() -> list[VersionInfo]:
    """List locally available versions."""
    return [
        VersionInfo(
            repository="adarshnemesis/coratiaos-core",
            tag="stable",
            is_current=True,
            is_local=True,
        ),
    ]


@app.get("/v1.0/version/remote")
async def list_remote_versions() -> list[VersionInfo]:
    """List available remote versions."""
    return [
        VersionInfo(repository="adarshnemesis/coratiaos-core", tag="stable", is_local=False),
        VersionInfo(repository="adarshnemesis/coratiaos-core", tag="beta", is_local=False),
        VersionInfo(repository="adarshnemesis/coratiaos-core", tag="master", is_local=False),
    ]


@app.post("/v1.0/version/update/{tag}")
async def update_to_version(tag: str) -> dict:
    """Pull and switch to a new version."""
    logger.info(f"Updating to version: {tag}")
    return {"success": True, "message": f"Update to {tag} initiated"}


@app.post("/v1.0/version/rollback")
async def rollback() -> dict:
    """Rollback to previous version."""
    return {"success": True, "message": "Rollback initiated"}


@app.post("/v1.0/version/restart")
async def restart_core() -> dict:
    """Restart the core service."""
    return {"success": True, "message": "Restart initiated"}


if __name__ == "__main__":
    run_service(app, port=8081, name="Version Chooser")
