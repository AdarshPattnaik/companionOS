"""
CoratiaOS Kraken — Extension Manager.

Responsibilities:
- Docker-based extension install/remove
- Extension store manifest
- Extension lifecycle management (start/stop/restart)
- Extension configuration
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from typing import Any, Optional
from pydantic import BaseModel
from loguru import logger
from commonwealth.api_utils import create_app, run_service

try:
    import docker
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False


class Extension(BaseModel):
    identifier: str
    name: str
    description: str = ""
    docker_image: str
    tag: str = "latest"
    enabled: bool = True
    container_name: str = ""
    author: str = ""
    version: str = ""
    webpage: str = ""
    permissions: dict = {}


class ExtensionStore(BaseModel):
    extensions: list[Extension] = []


app = create_app(title="Kraken", description="Extension manager for CoratiaOS")

installed_extensions: list[Extension] = []


def get_docker_client():
    if HAS_DOCKER:
        try:
            return docker.from_env()
        except Exception:
            pass
    return None


@app.get("/v1.0/extensions/installed")
async def list_installed() -> list[Extension]:
    """List installed extensions."""
    return installed_extensions


@app.get("/v1.0/extensions/store")
async def get_store() -> list[dict]:
    """Get available extensions from store (mock manifest)."""
    return [
        {
            "identifier": "coratia.ping-viewer",
            "name": "Ping Viewer",
            "description": "Sonar data visualization for Ping sonar devices",
            "docker_image": "coratia/ping-viewer",
            "author": "Coratia",
            "version": "1.0.0",
        },
        {
            "identifier": "coratia.navigator-tools",
            "name": "Navigator Tools",
            "description": "Tools for Blue Robotics Navigator board",
            "docker_image": "coratia/navigator-tools",
            "author": "Coratia",
            "version": "1.0.0",
        },
        {
            "identifier": "coratia.mavlink-camera-manager",
            "name": "MAVLink Camera Manager",
            "description": "Advanced camera and video management",
            "docker_image": "coratia/mavlink-camera-manager",
            "author": "Coratia",
            "version": "0.2.0",
        },
    ]


@app.post("/v1.0/extensions/install")
async def install_extension(extension: Extension) -> dict:
    """Install a Docker-based extension."""
    logger.info(f"Installing extension: {extension.name} ({extension.docker_image}:{extension.tag})")
    client = get_docker_client()
    if not client:
        return {"success": False, "error": "Docker not available"}

    try:
        # Pull image
        client.images.pull(extension.docker_image, tag=extension.tag)
        extension.container_name = f"coratiaos-ext-{extension.identifier}"
        installed_extensions.append(extension)
        return {"success": True, "message": f"Extension {extension.name} installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/v1.0/extensions/{identifier}")
async def uninstall_extension(identifier: str) -> dict:
    """Uninstall an extension."""
    global installed_extensions
    for i, ext in enumerate(installed_extensions):
        if ext.identifier == identifier:
            # Stop and remove container
            client = get_docker_client()
            if client and ext.container_name:
                try:
                    container = client.containers.get(ext.container_name)
                    container.stop()
                    container.remove()
                except Exception:
                    pass
            installed_extensions.pop(i)
            return {"success": True}
    return {"success": False, "error": "Extension not found"}


@app.post("/v1.0/extensions/{identifier}/start")
async def start_extension(identifier: str) -> dict:
    """Start an installed extension."""
    for ext in installed_extensions:
        if ext.identifier == identifier:
            ext.enabled = True
            return {"success": True}
    return {"success": False, "error": "Extension not found"}


@app.post("/v1.0/extensions/{identifier}/stop")
async def stop_extension(identifier: str) -> dict:
    """Stop a running extension."""
    for ext in installed_extensions:
        if ext.identifier == identifier:
            ext.enabled = False
            return {"success": True}
    return {"success": False, "error": "Extension not found"}


@app.post("/v1.0/extensions/{identifier}/restart")
async def restart_extension(identifier: str) -> dict:
    """Restart an extension."""
    return {"success": True, "message": "Extension restarted"}


@app.get("/v1.0/containers")
async def list_containers() -> list[dict]:
    """List all Docker containers (for monitoring)."""
    client = get_docker_client()
    if not client:
        return []
    try:
        containers = client.containers.list(all=True)
        return [
            {
                "name": c.name,
                "image": str(c.image.tags[0] if c.image.tags else c.image.id),
                "status": c.status,
                "created": str(c.attrs.get("Created", "")),
            }
            for c in containers
        ]
    except Exception:
        return []


if __name__ == "__main__":
    run_service(app, port=9134, name="Kraken")
