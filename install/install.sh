#!/bin/bash
# ============================================================
# CoratiaOS — Installation Script
# Install CoratiaOS on an existing Raspberry Pi OS system
# Usage: curl -fsSL https://raw.githubusercontent.com/coratia/CoratiaOS/main/install/install.sh | bash
# ============================================================

set -e

CORATIAOS_VERSION="${CORATIAOS_VERSION:-stable}"
CORATIAOS_REPO="coratia/coratiaos-core"

echo "=============================================="
echo "  CoratiaOS Installer"
echo "  Version: ${CORATIAOS_VERSION}"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Please run as root: sudo bash install.sh"
    exit 1
fi

# Check architecture
ARCH=$(uname -m)
echo "[INFO] Architecture: ${ARCH}"

# ── Install Docker ──
if ! command -v docker &> /dev/null; then
    echo "[INFO] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker pi || true
else
    echo "[INFO] Docker already installed"
fi

# ── Install pip dependencies ──
echo "[INFO] Installing Python dependencies..."
pip3 install --no-cache-dir docker requests 2>/dev/null || true

# ── Create directories ──
echo "[INFO] Creating directories..."
mkdir -p /opt/coratiaos/bootstrap
mkdir -p /root/.config/coratiaos
mkdir -p /var/logs/coratiaos
mkdir -p /usr/coratiaos/userdata

# ── Download and install bootstrap ──
echo "[INFO] Downloading CoratiaOS bootstrap..."
if [ -d "/tmp/coratiaos-install" ]; then
    rm -rf /tmp/coratiaos-install
fi

git clone --depth 1 https://github.com/coratia/CoratiaOS.git /tmp/coratiaos-install 2>/dev/null || {
    echo "[WARN] Git clone failed, creating bootstrap manually..."
    mkdir -p /tmp/coratiaos-install/bootstrap
}

cp -r /tmp/coratiaos-install/bootstrap/* /opt/coratiaos/bootstrap/ 2>/dev/null || true

# ── Default configuration ──
if [ ! -f /root/.config/coratiaos/startup.json ]; then
    cat > /root/.config/coratiaos/startup.json <<'EOF'
{
    "core": {
        "image": "coratia/coratiaos-core",
        "tag": "stable",
        "network": "host",
        "privileged": true,
        "binds": {
            "/run/udev": {"bind": "/run/udev", "mode": "ro"},
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"},
            "/root/.config/coratiaos": {"bind": "/root/.config/coratiaos", "mode": "rw"},
            "/var/logs/coratiaos": {"bind": "/var/logs/coratiaos", "mode": "rw"},
            "/usr/coratiaos": {"bind": "/usr/coratiaos", "mode": "rw"}
        }
    }
}
EOF
fi

# ── Configure network ──
echo "[INFO] Configuring network..."
if ! grep -q "CoratiaOS tether" /etc/dhcpcd.conf 2>/dev/null; then
    cat >> /etc/dhcpcd.conf <<'EOF'

# CoratiaOS tether interface
interface eth0
static ip_address=192.168.2.2/24
static routers=192.168.2.1
static domain_name_servers=8.8.8.8 8.8.4.4
EOF
fi

# ── Setup systemd service ──
echo "[INFO] Setting up systemd service..."
cat > /etc/systemd/system/coratiaos-bootstrap.service <<'EOF'
[Unit]
Description=CoratiaOS Bootstrap
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/coratiaos/bootstrap/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable coratiaos-bootstrap.service

# ── Set hostname ──
echo "coratiaos" > /etc/hostname
sed -i 's/raspberrypi/coratiaos/g' /etc/hosts 2>/dev/null || true

# ── Pull Docker image ──
echo "[INFO] Pulling CoratiaOS image (this may take a while)..."
docker pull "${CORATIAOS_REPO}:${CORATIAOS_VERSION}" || echo "[WARN] Image pull failed. Will retry on first boot."

# ── Cleanup ──
rm -rf /tmp/coratiaos-install

echo ""
echo "=============================================="
echo "  CoratiaOS installation complete!"
echo "  Reboot to start: sudo reboot"
echo "  Access dashboard: http://192.168.2.2"
echo "=============================================="
