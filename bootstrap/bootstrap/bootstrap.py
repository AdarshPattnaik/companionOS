"""
CoratiaOS Bootstrapper — Core container lifecycle manager.

Responsible for:
- Loading startup configuration
- Pulling/starting the core Docker container
- Watchdog monitoring (restart on failure)
- Graceful shutdown
"""
import asyncio
import json
import logging
import pathlib
import time
from typing import Any, Optional

import docker
import docker.errors
import requests

logger = logging.getLogger("coratiaos-bootstrap")

CORATIAOS_CONFIG_DIR = pathlib.Path("/root/.config/coratiaos")
STARTUP_CONFIG = CORATIAOS_CONFIG_DIR / "startup.json"
STARTUP_DEFAULT = pathlib.Path(__file__).parent.parent / "startup.json.default"

CORE_CONTAINER_NAME = "coratiaos-core"
WATCHDOG_POLL_SECONDS = 10
VERSION_CHOOSER_TIMEOUT = 300  # 5 minutes


class Bootstrapper:
    """Manages the CoratiaOS core container lifecycle."""

    def __init__(self) -> None:
        self.client = docker.from_env()
        self._running = True

    def _load_startup_config(self) -> dict[str, Any]:
        """Load startup configuration, falling back to defaults on error."""
        if STARTUP_CONFIG.exists():
            try:
                config = json.loads(STARTUP_CONFIG.read_text())
                if "core" in config:
                    return config
                logger.warning("Startup config missing 'core' key, resetting to defaults.")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Invalid startup config ({e}), resetting to defaults.")

        # Fall back to default
        default_config = json.loads(STARTUP_DEFAULT.read_text())
        CORATIAOS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        STARTUP_CONFIG.write_text(json.dumps(default_config, indent=2))
        return default_config

    def _reset_config_to_defaults(self) -> None:
        """Reset startup config to factory defaults."""
        default_config = json.loads(STARTUP_DEFAULT.read_text())
        CORATIAOS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        STARTUP_CONFIG.write_text(json.dumps(default_config, indent=2))
        logger.info("Configuration reset to defaults.")

    def is_running(self, container_name: str = CORE_CONTAINER_NAME) -> bool:
        """Check if a container is running."""
        try:
            containers = self.client.containers.list()
            return any(c.name == container_name for c in containers)
        except Exception as e:
            logger.error(f"Failed to check container status: {e}")
            return False

    def image_is_available_locally(self, image: str) -> bool:
        """Check if a Docker image exists locally."""
        try:
            images = self.client.images.list(image)
            return len(images) > 0
        except Exception as e:
            logger.error(f"Failed to check image availability: {e}")
            return False

    def is_version_chooser_online(self) -> bool:
        """Check if the version chooser service is responding."""
        try:
            response = requests.get(
                "http://localhost:8081/v1.0/version/current",
                timeout=5,
            )
            data = response.json()
            return "repository" in data
        except Exception:
            return False

    def start(self, config: dict[str, Any]) -> bool:
        """Start the core container from config."""
        core_config = config.get("core", {})
        image = core_config.get("image", "adarshnemesis/coratiaos-core:stable")
        tag = core_config.get("tag", "stable")
        full_image = f"{image}:{tag}" if ":" not in image else image

        logger.info(f"Starting CoratiaOS core: {full_image}")

        # Pull image if not available
        if not self.image_is_available_locally(full_image):
            logger.info(f"Pulling image {full_image}...")
            try:
                self.client.images.pull(full_image)
            except docker.errors.NotFound:
                logger.error(f"Image {full_image} not found.")
                self._reset_config_to_defaults()
                return False
            except docker.errors.APIError as e:
                logger.error(f"Failed to pull image: {e}")
                return False

        # Remove existing container if present
        try:
            existing = self.client.containers.get(CORE_CONTAINER_NAME)
            existing.stop(timeout=30)
            existing.remove()
        except docker.errors.NotFound:
            pass
        except Exception as e:
            logger.warning(f"Failed to remove old container: {e}")

        # Start new container
        try:
            network_mode = core_config.get("network", "host")
            binds = core_config.get("binds", {})
            privileged = core_config.get("privileged", True)

            self.client.containers.run(
                full_image,
                name=CORE_CONTAINER_NAME,
                network_mode=network_mode,
                privileged=privileged,
                volumes=binds,
                restart_policy={"Name": "unless-stopped"},
                detach=True,
            )
            logger.info("Core container started successfully.")
            return True
        except docker.errors.APIError as e:
            logger.error(f"Failed to start core container: {e}")
            self._reset_config_to_defaults()
            return False

    def remove(self) -> None:
        """Stop and remove the core container."""
        try:
            container = self.client.containers.get(CORE_CONTAINER_NAME)
            container.stop(timeout=60)
            container.remove()
            logger.info("Core container removed.")
        except docker.errors.NotFound:
            logger.info("Core container not found (already removed).")
        except Exception as e:
            logger.error(f"Failed to remove core container: {e}")

    async def run(self) -> None:
        """Main bootstrap loop — start core, then watchdog."""
        config = self._load_startup_config()

        if not self.start(config):
            logger.error("Initial start failed. Retrying with defaults...")
            self._reset_config_to_defaults()
            config = self._load_startup_config()
            if not self.start(config):
                logger.critical("Failed to start CoratiaOS core even with defaults.")
                return

        # Watchdog loop
        last_healthy_time = time.time()
        while self._running:
            await asyncio.sleep(WATCHDOG_POLL_SECONDS)

            if self.is_running():
                if self.is_version_chooser_online():
                    last_healthy_time = time.time()
                elif time.time() - last_healthy_time > VERSION_CHOOSER_TIMEOUT:
                    logger.warning("Core unresponsive for 5 minutes. Restarting...")
                    self.remove()
                    config = self._load_startup_config()
                    self.start(config)
                    last_healthy_time = time.time()
            else:
                logger.warning("Core container is not running. Restarting...")
                config = self._load_startup_config()
                self.start(config)
                last_healthy_time = time.time()
