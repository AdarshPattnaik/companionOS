# CoratiaOS Deployment Guide

## Option 1: Pre-built Raspberry Pi Image (Recommended)

1. Download the latest `coratiaos-vX.X.X.zip` from [Releases](https://github.com/coratia/CoratiaOS/releases)
2. Flash to an SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
3. Insert SD card into Raspberry Pi 4
4. Connect ethernet cable between RPi and your computer
5. Power on the RPi
6. Wait 2-3 minutes for first boot
7. Open browser → `http://192.168.2.2`

## Option 2: Install Script

On an existing Raspberry Pi OS Bullseye:

```bash
sudo curl -fsSL https://raw.githubusercontent.com/coratia/CoratiaOS/main/install/install.sh | bash
sudo reboot
```

## Option 3: Manual Installation

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Clone and setup
git clone https://github.com/coratia/CoratiaOS.git /opt/coratiaos
cd /opt/coratiaos

# 3. Configure network
sudo cat >> /etc/dhcpcd.conf <<EOF
interface eth0
static ip_address=192.168.2.2/24
EOF

# 4. Build or pull
docker pull coratia/coratiaos-core:stable

# 5. Start bootstrap
python3 bootstrap/main.py &

# 6. Reboot
sudo reboot
```

## Network Configuration

| Setting           | Value              |
| ----------------- | ------------------ |
| ROV IP (RPi)      | 192.168.2.2        |
| GCS IP (computer) | 192.168.2.1        |
| Subnet            | 255.255.255.0      |
| Dashboard         | http://192.168.2.2 |
| MAVLink UDP       | 192.168.2.1:14550  |

### Computer Setup

Set your ethernet adapter to:

- IP: `192.168.2.1`
- Subnet: `255.255.255.0`
- Gateway: (leave blank)

## Updating

From the web dashboard: **Version** → **Check Updates** → **Update**

Or via command line:

```bash
docker pull coratia/coratiaos-core:stable
sudo systemctl restart coratiaos-bootstrap
```

## Troubleshooting

| Issue                   | Solution                                                          |
| ----------------------- | ----------------------------------------------------------------- |
| Can't reach 192.168.2.2 | Check ethernet cable and computer IP (must be 192.168.2.1)        |
| Dashboard doesn't load  | Wait 2-3 min after boot, check `docker ps`                        |
| Services not starting   | Check logs: `docker logs coratiaos-core`                          |
| Bootstrap failure       | Reset config: `rm /root/.config/coratiaos/startup.json && reboot` |
