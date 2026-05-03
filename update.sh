#!/bin/bash
set -euo pipefail

echo "🚀 Zmanim PRO updater"

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"
SERVICE_NAME="zmanim"

log() { echo -e "👉 $1"; }

download() {
  local url=$1
  local file=$2

  log "Downloading $file..."
  if ! curl -fsSL "$url" -o "$file"; then
    echo "❌ Failed to download $file"
    exit 1
  fi
}

# ---------------- STOP SERVICE ----------------
log "Stopping service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

# ---------------- DOWNLOAD FILES ----------------
log "Updating project files..."

cd "$APP_DIR"

download "$REPO/server.py" server.py
download "$REPO/config.json" config.json
download "$REPO/version.txt" version.txt
download "$REPO/yom_tov.py" yom_tov.py
download "$REPO/requirements.txt" requirements.txt

chmod +x update.sh

# ---------------- PYTHON ENV ----------------
log "Updating Python dependencies..."
$APP_DIR/zmanim-env/bin/pip install --upgrade pip setuptools wheel
$APP_DIR/zmanim-env/bin/pip install --no-cache-dir -r requirements.txt

# Fix missing packages
$APP_DIR/zmanim-env/bin/pip install --no-cache-dir convertdate flask

# ---------------- RESTART SERVICE ----------------
log "Restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

sleep 3

# ---------------- HEALTH CHECK ----------------
log "Health check..."

URL="http://127.0.0.1:5000/zmanim?date=$(date +%F)"

if curl -fsS "$URL" >/dev/null; then
  echo "✅ UPDATE OK - API WORKING"
else
  echo "❌ UPDATE FAILED"
  echo "👉 journalctl -u $SERVICE_NAME -e"
  exit 1
fi

echo "🎉 DONE"
echo "👉 API: http://192.168.178.114:5000/zmanim"
