#!/bin/bash
# ============================================================
# CoratiaOS — Main startup script
# Starts all services, nginx, and monitoring
# ============================================================

set -e

CORATIAOS_HOME="/home/coratiaos"
LOG_DIR="/var/logs/coratiaos"
CONFIG_DIR="/root/.config/coratiaos"

mkdir -p "$LOG_DIR" "$CONFIG_DIR"

echo "========================================"
echo "  CoratiaOS v1.0.0"
echo "  The ROV Operating System by Coratia"
echo "========================================"

# Start nginx
echo "[CoratiaOS] Starting nginx..."
nginx -g "daemon on;" || echo "[WARN] nginx failed to start"

# Start ttyd (web terminal) on port 8088
echo "[CoratiaOS] Starting web terminal..."
ttyd -p 8088 -W bash &> "$LOG_DIR/ttyd.log" &

# Service list with ports
declare -A SERVICES=(
    ["ardupilot_manager"]="8000"
    ["video_manager"]="6020"
    ["helper"]="6040"
    ["commander"]="6010"
    ["wifi_manager"]="6050"
    ["cable_guy"]="9090"
    ["kraken"]="9134"
    ["version_chooser"]="8081"
    ["log_manager"]="6065"
    ["file_browser"]="7070"
    ["nmea_injector"]="6030"
)

# Start each service
for service in "${!SERVICES[@]}"; do
    port="${SERVICES[$service]}"
    service_dir="$CORATIAOS_HOME/services/$service"
    
    if [ -d "$service_dir" ]; then
        echo "[CoratiaOS] Starting $service on port $port..."
        "$CORATIAOS_HOME/run-service.sh" "$service" "$port" &> "$LOG_DIR/${service}.log" &
    else
        echo "[WARN] Service $service not found at $service_dir"
    fi
done

echo "[CoratiaOS] All services started."
echo "[CoratiaOS] Dashboard available at http://localhost:80"

# Health monitoring loop
while true; do
    sleep 30
done
