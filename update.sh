#!/bin/bash
set -euo pipefail

echo "🚀 Zmanim PRO ULTRA updater v2"

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"
SERVICE_NAME="zmanim"

log() { echo -e "👉 $1"; }

download() {
  local url=$1
  local file=$2

  log "Downloading $file"
  curl -fsSL "$url" -o "$file"
}

# ---------------- STOP SERVICE ----------------
log "Stopping service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

# ---------------- VERIFY APP DIR ----------------
if [ ! -d "$APP_DIR" ]; then
  echo "❌ /opt/zmanim missing → run install.sh first"
  exit 1
fi

cd "$APP_DIR"

# ---------------- SYNC FILES ----------------
log "Syncing GitHub files..."

FILES=(
  "server.py"
  "config.json"
  "version.txt"
  "yom_tov.py"
  "requirements.txt"
)

for f in "${FILES[@]}"; do
  download "$REPO/$f" "$f"
done

chmod +x update.sh

# ---------------- VERSION CHECK ----------------
LOCAL_VERSION=$(cat version.txt 2>/dev/null || echo "unknown")
REMOTE_VERSION=$(curl -fsSL "$REPO/version.txt")

echo "📦 Local:  $LOCAL_VERSION"
echo "📦 Remote: $REMOTE_VERSION"

if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ]; then
  echo "✔ Already up to date"
else
  echo "⬆️ Updating to $REMOTE_VERSION"
fi

# ---------------- VENV HEALTH CHECK ----------------
log "Checking Python environment..."

VENV="$APP_DIR/zmanim-env"

if [ ! -d "$VENV" ]; then
  echo "⚠️ venv missing → recreating..."
  python3 -m venv "$VENV"
fi

# Always repair pip environment (important fix)
$VENV/bin/pip install --upgrade pip setuptools wheel

# Install dependencies safely
log "Installing requirements..."
$VENV/bin/pip install --no-cache-dir -r requirements.txt

# HARD FIX: prevent runtime crashes
$VENV/bin/pip install --no-cache-dir flask convertdate

# ---------------- SYSTEMD RELOAD ----------------
log "Restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

sleep 3

# ---------------- HEALTH CHECK ----------------
log "Health check..."

URL="http://127.0.0.1:5000/zmanim?date=$(date +%F)"

if curl -fsS "$URL" >/dev/null; then
  echo "✅ UPDATE SUCCESS"
else
  echo "❌ UPDATE FAILED - CHECK LOGS"
  journalctl -u $SERVICE_NAME -n 50 --no-pager
  exit 1
fi

echo ""
echo "🎉 DONE"
echo "👉 API: http://192.168.178.114:5000/zmanim"
