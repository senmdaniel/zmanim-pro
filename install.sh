#!/bin/bash
set -euo pipefail

echo "🚀 Zmanim PRO installer v4 (bulletproof)"

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"
SERVICE_NAME="zmanim"
USER_NAME="mjd"

# ---------- helpers ----------
log() { echo -e "👉 $1"; }

download() {
  local url=$1
  local file=$2

  log "Downloading $file"

  for i in 1 2 3; do
    if curl -fsSL --retry 3 --retry-delay 2 "$url" -o "$file"; then
      return 0
    fi
    echo "⚠️ retry $i failed for $file"
    sleep 2
  done

  echo "❌ Failed to download $file"
  exit 1
}

# ---------- system ----------
log "Updating system..."
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

# ---------- clean install ----------
log "Cleaning old install..."
sudo rm -rf "$APP_DIR"

log "Creating app directory..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER_NAME:$USER_NAME" "$APP_DIR"

cd "$APP_DIR"

# ---------- download ----------
log "Downloading project files..."

download "$REPO/server.py" server.py
download "$REPO/config.json" config.json
download "$REPO/version.txt" version.txt
download "$REPO/update.sh" update.sh

chmod +x update.sh

# ---------- python ----------
log "Creating Python environment..."
python3 -m venv zmanim-env

log "Upgrading pip..."
./zmanim-env/bin/pip install --upgrade pip

log "Installing dependencies..."
./zmanim-env/bin/pip install flask zmanim convertdate

# ---------- systemd ----------
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
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ---------- start service ----------
log "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# ---------- health check ----------
log "Testing API..."
sleep 4

URL="http://localhost:5000/zmanim?date=$(date +%F)"

if curl -fsS "$URL" >/dev/null; then
  echo "✅ INSTALL SUCCESS - API WORKING"
else
  echo "❌ INSTALL FAILED - API NOT RESPONDING"
  echo "👉 run: journalctl -u $SERVICE_NAME -e"
  exit 1
fi

echo ""
echo "🎉 DONE"
echo "👉 API: http://localhost:5000/zmanim"
