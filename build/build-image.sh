#!/bin/bash
# ============================================================
# CoratiaOS — Local Build Script
# Builds the flashable Raspberry Pi image on a Linux machine
# 
# Requirements:
#   - Linux (native or WSL2)
#   - Docker installed and running
#   - sudo access
#   - ~10GB free disk space
#
# Usage:
#   chmod +x build/build-image.sh
#   sudo ./build/build-image.sh
#
# Output:
#   CoratiaOS-vX.X.X-YYYYMMDD.zip (flashable with Raspberry Pi Imager)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$SCRIPT_DIR"
VERSION="${CORATIAOS_VERSION:-1.0.0}"
DATE=$(date +%Y%m%d)
OUTPUT_NAME="CoratiaOS-v${VERSION}-${DATE}"

echo "=============================================="
echo "  CoratiaOS Image Builder"
echo "  Version: ${VERSION}"
echo "  Date:    ${DATE}"
echo "=============================================="

# Check requirements
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Must run as root: sudo $0"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is required. Install: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# ── Step 1: Build Frontend ──
echo ""
echo "[1/4] Building frontend..."
cd "$PROJECT_ROOT/core/frontend"
if command -v npm &> /dev/null; then
    npm ci --no-audit 2>/dev/null
    npm run build
else
    echo "[WARN] npm not found. Skipping frontend build."
    echo "       Install Node.js 18+ or pre-build the frontend."
fi

# ── Step 2: Build Docker Image (ARM) ──
echo ""
echo "[2/4] Building Docker image for ARM..."
cd "$PROJECT_ROOT"

# Enable QEMU for cross-platform builds
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes 2>/dev/null || true

# Build ARM image
docker buildx create --name coratiaos-builder --use 2>/dev/null || docker buildx use coratiaos-builder
docker buildx build \
    --platform linux/arm/v7 \
    -f core/Dockerfile \
    -t coratia/coratiaos-core:stable \
    --output type=docker,dest="$BUILD_DIR/docker-image/coratiaos-core.tar" \
    .

echo "   Docker image saved to: $BUILD_DIR/docker-image/coratiaos-core.tar"

# ── Step 3: Install pimod ──
echo ""
echo "[3/4] Setting up pimod..."
PIMOD_DIR="/tmp/pimod"
if [ ! -d "$PIMOD_DIR" ]; then
    apt-get update -qq
    apt-get install -y -qq binfmt-support kpartx qemu-user-static parted zerofree wget xz-utils unzip
    git clone --depth 1 https://github.com/Nature40/pimod.git "$PIMOD_DIR"
fi

# ── Step 4: Build Pi Image ──
echo ""
echo "[4/4] Building Raspberry Pi image..."
cd "$PROJECT_ROOT"
"$PIMOD_DIR/pimod.sh" "$BUILD_DIR/coratiaos.Pifile"

# Find the output image
IMG_FILE=$(ls *.img 2>/dev/null | head -1)
if [ -z "$IMG_FILE" ]; then
    IMG_FILE=$(ls "$BUILD_DIR"/*.img 2>/dev/null | head -1)
fi

if [ -z "$IMG_FILE" ]; then
    echo "[ERROR] No .img file found after build!"
    exit 1
fi

# ── Compress ──
echo ""
echo "[✓] Compressing image..."
ZIP_FILE="${OUTPUT_NAME}.zip"
zip -9 "$ZIP_FILE" "$IMG_FILE"
rm -f "$IMG_FILE"

SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo ""
echo "=============================================="
echo "  BUILD COMPLETE!"
echo "  Output: $ZIP_FILE ($SIZE)"
echo ""
echo "  Flash with Raspberry Pi Imager:"
echo "    1. Open Raspberry Pi Imager"
echo "    2. Choose OS → Use Custom → select $ZIP_FILE"
echo "    3. Choose Storage → your SD card"
echo "    4. Click Write"
echo ""
echo "  After flashing:"
echo "    - Set your computer IP to 192.168.2.1"
echo "    - Connect ethernet to the RPi"
echo "    - Open http://192.168.2.2"
echo "=============================================="
