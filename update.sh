#!/bin/bash
set -euo pipefail

echo "🚀 Zmanim PRO updater (fix convertdate issue)"

APP_DIR="/opt/zmanim"
SERVICE_NAME="zmanim"
VENV="$APP_DIR/zmanim-env"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

log() { echo -e "👉 $1"; }

download() {
    local url=$1
    local file=$2
    log "Downloading $file"
    curl -fsSL "$url" -o "$file"
}

# Stop service
log "Stopping service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

# Update files from GitHub
FILES=("server.py" "yom_tov.py" "requirements.txt" "version.txt" "config.json")
for f in "${FILES[@]}"; do
    download "$REPO/$f" "$APP_DIR/$f"
done

# Ensure venv exists
if [ ! -d "$VENV" ]; then
    log "⚠️ venv missing → creating..."
    python3 -m venv "$VENV"
fi

# Upgrade pip and install dependencies inside venv
log "Installing Python dependencies in venv..."
"$VENV/bin/pip" install --upgrade pip setuptools wheel
"$VENV/bin/pip" install -r "$APP_DIR/requirements.txt"

# HARD FIX: install convertdate explicitly
"$VENV/bin/pip" install --no-cache-dir convertdate

# Restart service using correct venv
log "Restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart $SERVICE_NAME

sleep 3

# Health check
URL="http://127.0.0.1:5000/zmanim?date=$(date +%F)"
if curl -fsS "$URL" >/dev/null; then
    echo "✅ UPDATE SUCCESS - API WORKING"
else
    echo "❌ UPDATE FAILED - CHECK LOGS"
    journalctl -u $SERVICE_NAME -n 50 --no-pager
    exit 1
fi

echo "🎉 DONE"
