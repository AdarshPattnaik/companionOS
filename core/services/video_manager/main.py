"""
CoratiaOS Video Manager — Camera detection and video streaming.

Responsibilities:
- USB and CSI camera detection
- Video stream creation and management
- GStreamer pipeline control
- Stream configuration (resolution, bitrate, codec)
"""
import os
import subprocess
from enum import Enum
from typing import Any, Optional

from fastapi import HTTPException
from loguru import logger
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))

from commonwealth.api_utils import create_app, run_service


# ── Models ──
class VideoCodec(str, Enum):
    H264 = "h264"
    H265 = "h265"
    MJPEG = "mjpeg"


class VideoSource(BaseModel):
    name: str
    device: str  # e.g., "/dev/video0"
    source_type: str  # "usb" or "csi"
    resolutions: list[str] = ["1920x1080", "1280x720", "640x480"]


class VideoStream(BaseModel):
    name: str
    source: str  # device path
    width: int = 1280
    height: int = 720
    bitrate: int = 5000  # kbps
    framerate: int = 30
    codec: VideoCodec = VideoCodec.H264
    endpoint: str = "rtsp://0.0.0.0:8554/video0"
    enabled: bool = True


# ── State ──
class VideoManagerState:
    def __init__(self):
        self.sources: list[VideoSource] = []
        self.streams: list[VideoStream] = []
        self._processes: dict[str, subprocess.Popen] = {}

    def detect_cameras(self) -> list[VideoSource]:
        """Detect available video devices."""
        self.sources = []
        # Check /dev/video* devices
        try:
            import glob
            for device in sorted(glob.glob("/dev/video*")):
                try:
                    result = subprocess.run(
                        ["v4l2-ctl", "--device", device, "--all"],
                        capture_output=True, text=True, timeout=5,
                    )
                    name = "Unknown Camera"
                    for line in result.stdout.split("\n"):
                        if "Card type" in line:
                            name = line.split(":")[1].strip()
                            break

                    self.sources.append(VideoSource(
                        name=name,
                        device=device,
                        source_type="usb",
                    ))
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Camera detection failed: {e}")

        # Check CSI camera
        if os.path.exists("/dev/video0") or os.path.exists("/boot/config.txt"):
            try:
                result = subprocess.run(
                    ["vcgencmd", "get_camera"],
                    capture_output=True, text=True, timeout=5,
                )
                if "detected=1" in result.stdout:
                    self.sources.append(VideoSource(
                        name="CSI Camera",
                        device="csi://0",
                        source_type="csi",
                    ))
            except Exception:
                pass

        return self.sources


state = VideoManagerState()

# ── App ──
app = create_app(
    title="Video Manager",
    description="Camera detection and video streaming management",
)


@app.get("/v1.0/cameras")
async def list_cameras() -> list[VideoSource]:
    """Detect and list available cameras."""
    return state.detect_cameras()


@app.get("/v1.0/streams")
async def list_streams() -> list[VideoStream]:
    """List active video streams."""
    return state.streams


@app.post("/v1.0/streams")
async def create_stream(stream: VideoStream) -> VideoStream:
    """Create a new video stream."""
    state.streams.append(stream)
    logger.info(f"Stream created: {stream.name} ({stream.source} → {stream.endpoint})")
    return stream


@app.delete("/v1.0/streams/{name}")
async def delete_stream(name: str) -> dict:
    """Delete a video stream."""
    for i, s in enumerate(state.streams):
        if s.name == name:
            state.streams.pop(i)
            # Stop GStreamer process if running
            if name in state._processes:
                state._processes[name].terminate()
                del state._processes[name]
            return {"deleted": True}
    raise HTTPException(404, "Stream not found")


@app.put("/v1.0/streams/{name}")
async def update_stream(name: str, stream: VideoStream) -> VideoStream:
    """Update a video stream configuration."""
    for i, s in enumerate(state.streams):
        if s.name == name:
            state.streams[i] = stream
            return stream
    raise HTTPException(404, "Stream not found")


@app.get("/v1.0/streams/{name}/snapshot")
async def get_snapshot(name: str) -> dict:
    """Get a snapshot URL from a stream (placeholder)."""
    return {"url": f"/video/snapshot/{name}.jpg", "available": False}


if __name__ == "__main__":
    run_service(app, port=6020, name="Video Manager")
