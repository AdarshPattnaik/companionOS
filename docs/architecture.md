# CoratiaOS Architecture

## Overview

CoratiaOS is a Docker-based operating system for managing underwater ROVs. It runs on Raspberry Pi 4 with Raspberry Pi OS Bullseye as the base.

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Web Browser (Port 80)                    │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                      Nginx Reverse Proxy                     │
│  Routes: /, /ardupilot-manager, /video, /helper, /wifi, etc  │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                  CoratiaOS Core Container                     │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │  Ardupilot   │  │   Video     │  │   System Helper      │ │
│  │  Manager     │  │   Manager   │  │   (CPU/RAM/Temp)     │ │
│  │  :8000       │  │   :6020     │  │   :6040              │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │  Commander   │  │   WiFi      │  │   Cable Guy          │ │
│  │  :6010       │  │   Manager   │  │   (Ethernet)         │ │
│  │              │  │   :6050     │  │   :9090              │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │  Kraken      │  │   Version   │  │   Log Manager        │ │
│  │  (Extensions)│  │   Chooser   │  │   :6065              │ │
│  │  :9134       │  │   :8081     │  │                      │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │  File Browser│  │   NMEA      │  │   Web Terminal       │ │
│  │  :7070       │  │   Injector  │  │   (ttyd) :8088       │ │
│  │              │  │   :6030     │  │                      │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          Vue 3 Frontend (Static, served by nginx)      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                    Bootstrap Container                        │
│          Manages core container lifecycle + watchdog          │
└──────────────────────────────────────────────────────────────┘
```

## Boot Sequence

1. **Raspberry Pi boots** → Raspberry Pi OS Bullseye starts
2. **Systemd** → starts `coratiaos-bootstrap.service`
3. **Bootstrap** → reads `startup.json`, pulls/starts core Docker container
4. **Core container** → `start-coratiaos.sh` launches all services + nginx
5. **Nginx** → serves frontend on port 80, proxies all service APIs
6. **User** → connects via browser at `http://192.168.2.2`

## Service Communication

- All services are **FastAPI** (Python) apps running on localhost with distinct ports
- Services communicate via HTTP REST APIs on `127.0.0.1`
- Nginx proxies external requests to the correct service
- WebSocket connections supported for telemetry and live system stats

## Key Technologies

| Component  | Technology                      |
| ---------- | ------------------------------- |
| Base OS    | Raspberry Pi OS Bullseye        |
| Containers | Docker                          |
| Backend    | Python 3.11 + FastAPI + uvicorn |
| Frontend   | Vue 3 + Vite                    |
| MAVLink    | pymavlink                       |
| Video      | GStreamer                       |
| Proxy      | Nginx                           |
| Terminal   | ttyd                            |
| Build      | Pimod                           |
| CI/CD      | GitHub Actions                  |

## Directory Structure

```
CoratiaOS/
├── bootstrap/          # Bootstrap system (container lifecycle)
├── core/
│   ├── Dockerfile      # Multi-stage build
│   ├── compose/        # Docker Compose for dev
│   ├── configuration/  # Nginx config
│   ├── frontend/       # Vue 3 dashboard
│   ├── libs/           # Shared Python libraries
│   │   ├── commonwealth/  # Settings, API utils, MAVLink
│   │   └── bridges/       # Serial port helpers
│   └── services/       # 11 FastAPI microservices
├── build/              # Pimod build files
├── install/            # Installation scripts
├── .github/workflows/  # CI/CD
└── docs/               # Documentation
```
