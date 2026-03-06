#!/bin/bash
# ============================================================
# CoratiaOS — Service runner
# Usage: run-service.sh <service_name> <port>
# ============================================================

SERVICE_NAME="$1"
PORT="$2"
SERVICE_DIR="/home/coratiaos/services/$SERVICE_NAME"

if [ ! -d "$SERVICE_DIR" ]; then
    echo "[ERROR] Service directory not found: $SERVICE_DIR"
    exit 1
fi

if [ ! -f "$SERVICE_DIR/main.py" ]; then
    echo "[ERROR] main.py not found in: $SERVICE_DIR"
    exit 1
fi

echo "[CoratiaOS] Starting service: $SERVICE_NAME (port $PORT)"
cd "$SERVICE_DIR"

# Run with uvicorn if it's a FastAPI service
exec python main.py --port "$PORT"
