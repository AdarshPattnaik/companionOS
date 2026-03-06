# ============================================================
# CoratiaOS Core — Multi-stage Docker build
# ============================================================
# Stage 1: Build frontend
# Stage 2: Create runtime with Python services + built frontend
# ============================================================

# ------- Stage 1: Frontend Build -------
FROM node:18-bullseye-slim AS frontend-builder

WORKDIR /build/frontend
COPY core/frontend/package.json core/frontend/package-lock.json* ./
RUN npm ci --no-audit
COPY core/frontend/ ./
RUN npm run build

# ------- Stage 2: Runtime -------
FROM python:3.11-slim-bullseye

LABEL maintainer="Coratia <dev@coratia.com>"
LABEL description="CoratiaOS Core — ROV Operating System"
LABEL version="1.0.0"

# System dependencies — split into required and optional
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    iproute2 \
    iputils-ping \
    curl \
    wget \
    git \
    udev \
    sudo \
    openssh-client \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Optional system packages (may fail on some architectures — that's OK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsmasq \
    avahi-daemon \
    i2c-tools \
    v4l-utils \
    wpa-supplicant \
    wireless-tools \
    iw \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    libgstreamer1.0-0 \
    || true \
    && rm -rf /var/lib/apt/lists/*

# Install ttyd (web terminal) from GitHub releases
RUN ARCH=$(dpkg --print-architecture) && \
    curl -fsSL "https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.${ARCH}" \
    -o /usr/local/bin/ttyd && \
    chmod +x /usr/local/bin/ttyd \
    || echo "ttyd install skipped (unsupported arch)"

# Python dependencies
COPY core/libs /home/coratiaos/libs
RUN pip install --no-cache-dir \
    fastapi[all] \
    uvicorn[standard] \
    aiohttp \
    aiofiles \
    docker \
    psutil \
    pyserial \
    pymavlink \
    loguru \
    pydantic \
    requests \
    websockets \
    netifaces \
    packaging \
    appdirs

# Install local libraries
RUN pip install --no-cache-dir \
    /home/coratiaos/libs/commonwealth \
    /home/coratiaos/libs/bridges

# Copy services
COPY core/services /home/coratiaos/services
COPY core/run-service.sh /home/coratiaos/run-service.sh
COPY core/start-coratiaos.sh /home/coratiaos/start-coratiaos.sh
RUN chmod +x /home/coratiaos/run-service.sh /home/coratiaos/start-coratiaos.sh

# Copy built frontend
COPY --from=frontend-builder /build/frontend/dist /home/coratiaos/frontend

# Copy nginx config
COPY core/configuration/nginx /etc/nginx/conf.d/

# Copy configuration files
COPY core/configuration /home/coratiaos/configuration

WORKDIR /home/coratiaos

EXPOSE 80 8080 6020 6040 6050 9090 9134

ENTRYPOINT ["/home/coratiaos/start-coratiaos.sh"]
