# CoratiaOS Developer Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Docker and Docker Compose (optional, for container testing)
- Git

## Project Setup

```bash
git clone https://github.com/coratia/CoratiaOS.git
cd CoratiaOS
```

## Frontend Development

```bash
cd core/frontend
npm install
npm run dev      # Starts dev server on http://localhost:2511
npm run build    # Production build to dist/
```

The Vite dev server proxies all API requests to their respective backend ports (see `vite.config.js`).

### Frontend Structure

```
core/frontend/src/
├── main.js              # App entry
├── App.vue              # Root layout (sidebar + topbar)
├── router/index.js      # Routes with lazy loading
├── assets/main.css      # Design system (CSS variables)
└── views/               # 12 page components
    ├── DashboardView.vue
    ├── VehicleView.vue
    ├── EndpointsView.vue
    ├── VideoView.vue
    ├── ParametersView.vue
    ├── ExtensionsView.vue
    ├── NetworkView.vue
    ├── SystemView.vue
    ├── LogsView.vue
    ├── FilesView.vue
    ├── TerminalView.vue
    └── VersionView.vue
```

## Backend Service Development

Each service is a standalone FastAPI application. To run a single service:

```bash
cd core/services/helper
pip install -r ../../libs/commonwealth/requirements.txt  # if needed
pip install fastapi uvicorn psutil loguru
python main.py --port 6040
```

Then access the Swagger docs at `http://localhost:6040/v1.0/docs`.

### Creating a New Service

1. Create `core/services/my_service/main.py`:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "libs", "commonwealth", "src"))
from commonwealth.api_utils import create_app, run_service

app = create_app(title="My Service", description="Does something useful")

@app.get("/v1.0/status")
async def get_status():
    return {"status": "ok"}

if __name__ == "__main__":
    run_service(app, port=XXXX, name="My Service")
```

2. Add nginx proxy rule in `core/configuration/nginx/coratiaos.conf`
3. Add to the service list in `core/start-coratiaos.sh`
4. Add frontend view in `core/frontend/src/views/`
5. Add route in `core/frontend/src/router/index.js`

### Shared Libraries

- **Commonwealth** (`core/libs/commonwealth/`): Settings manager, API helpers, MAVLink wrapper
- **Bridges** (`core/libs/bridges/`): Serial port detection and FC identification

## Service Ports

| Service             | Port |
| ------------------- | ---- |
| Ardupilot Manager   | 8000 |
| Commander           | 6010 |
| Video Manager       | 6020 |
| NMEA Injector       | 6030 |
| System Helper       | 6040 |
| WiFi Manager        | 6050 |
| Log Manager         | 6065 |
| File Browser        | 7070 |
| Version Chooser     | 8081 |
| Web Terminal (ttyd) | 8088 |
| Cable Guy           | 9090 |
| Kraken              | 9134 |

## Docker Build

```bash
# Build core image
docker build -t adarshnemesis/coratiaos-core:local -f core/Dockerfile .

# Run with compose
cd core/compose
docker compose up
```

## Raspberry Pi Image Build

Requires Linux with pimod installed:

```bash
sudo pimod.sh build/coratiaos.Pifile
```
