#!/bin/bash
set -euo pipefail

echo "🚀 Zmanim PRO installer v6 (FIXED DEPLOY)"

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"
SERVICE_NAME="zmanim"
USER_NAME="mjd"

log() { echo -e "👉 $1"; }

download() {
  local url=$1
  local file=$2

  log "Downloading $file"

  if ! curl -fsSL "$url" -o "$file"; then
    echo "❌ Failed: $file"
    exit 1
  fi
}

# ---------------- SYSTEM ----------------
log "Installing system packages..."
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

# ---------------- STOP SERVICE ----------------
log "Stopping old service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
sudo systemctl disable $SERVICE_NAME 2>/dev/null || true

# ---------------- CLEAN INSTALL ----------------
log "Cleaning /opt..."
sudo rm -rf "$APP_DIR"
sudo rm -f /etc/systemd/system/${SERVICE_NAME}.service
sudo systemctl daemon-reload

# ---------------- CREATE APP ----------------
log "Creating app directory..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER_NAME:$USER_NAME" "$APP_DIR"
cd "$APP_DIR"

# ---------------- DOWNLOAD FILES ----------------
log "Downloading latest GitHub files..."

download "$REPO/server.py" server.py
download "$REPO/config.json" config.json
download "$REPO/version.txt" version.txt
download "$REPO/update.sh" update.sh
download "$REPO/requirements.txt" requirements.txt
download "$REPO/yom_tov.py" yom_tov.py

chmod +x update.sh

# ---------------- PYTHON ENV ----------------
log "Creating fresh virtualenv..."
python3 -m venv zmanim-env

log "Upgrading pip..."
./zmanim-env/bin/pip install --upgrade pip setuptools wheel

log "Installing dependencies (FORCED)..."
./zmanim-env/bin/pip install --no-cache-dir -r requirements.txt

# 🔥 HARD FIX: ensure missing packages never break server
./zmanim-env/bin/pip install convertdate flask

# ---------------- SYSTEMD ----------------
log "Creating systemd service..."

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Zmanim PRO
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/zmanim-env/bin/python $APP_DIR/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# ---------------- START ----------------
log "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

sleep 3

# ---------------- HEALTH CHECK ----------------
log "Health check..."

URL="http://127.0.0.1:5000/zmanim?date=$(date +%F)"

if curl -fsS "$URL" >/dev/null; then
  echo "✅ INSTALL OK - API WORKING"
else
  echo "❌ INSTALL FAILED"
  echo "👉 journalctl -u $SERVICE_NAME -e"
  exit 1
fi

echo ""
echo "🎉 DONE"
echo "👉 API: http://192.168.178.114:5000/zmanim"
