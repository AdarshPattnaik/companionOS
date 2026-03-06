# CoratiaOS

**The modular operating system for underwater ROV control, by Coratia.**

CoratiaOS is a Docker-based, microservice-oriented platform for managing underwater Remotely Operated Vehicles (ROVs). It runs on Raspberry Pi 4 and provides a browser-based interface for vehicle control, telemetry, video streaming, and system management.

## Features

- 🔧 **MAVLink Communication** — Full MAVLink routing with ArduSub/PX4 support
- 📹 **Video Streaming** — Low-latency camera feeds (USB + CSI) via RTSP/WebRTC
- 🌐 **Web Dashboard** — Modern dark-themed browser interface
- 🐋 **Docker Microservices** — Modular, independently updatable services
- 🔌 **Extension System** — Install additional capabilities as Docker containers
- 📡 **Network Management** — WiFi, Ethernet, and hotspot configuration
- 📊 **System Monitoring** — CPU, RAM, temperature, and disk metrics
- 🔄 **OTA Updates** — Over-the-air update system with rollback

## Architecture

CoratiaOS uses a modular microservice architecture where each service runs as a Python/FastAPI application inside a Docker container, orchestrated by a bootstrap system and fronted by nginx.

```
Browser → nginx (port 80)
              ├── /  → Frontend (Vue 3 dashboard)
              ├── /mavlink2rest → MAVLink REST API
              ├── /ardupilot-manager → Vehicle management
              ├── /video → Video streaming
              ├── /helper → System information
              ├── /commander → Vehicle commands
              ├── /wifi → WiFi management
              ├── /ethernet → Network config
              ├── /kraken → Extension manager
              └── /file-browser → File management
```

## Quick Start

### Development (Docker Compose)

```bash
git clone https://github.com/coratia/CoratiaOS.git
cd CoratiaOS/core/compose
docker compose up
```

### Raspberry Pi Installation

Download the latest CoratiaOS image from releases, flash to SD card using Raspberry Pi Imager, and connect to `http://192.168.2.2`.

### Manual Installation

```bash
curl -fsSL https://raw.githubusercontent.com/coratia/CoratiaOS/main/install/install.sh | bash
```

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### Frontend Development

```bash
cd core/frontend
npm install
npm run dev
```

### Backend Service Development

```bash
cd core/services/<service_name>
pip install -r requirements.txt
python main.py
```

## Target Hardware

- **Primary**: Raspberry Pi 4 (2GB+ RAM)
- **Base OS**: Raspberry Pi OS Bullseye
- **Supported Architectures**: ARM v7, ARM64

## License

Copyright © 2024 Coratia. All rights reserved.
