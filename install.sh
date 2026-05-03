#!/bin/bash
set -euo pipefail

echo "🚀 Zmanim PRO installer v2 (stable)"

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"
SERVICE_NAME="zmanim"
USER_NAME="$(whoami)"

echo "📦 Updating system..."
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

echo "📁 Preparing application directory..."

# maak folder
sudo mkdir -p "$APP_DIR"

# geef ownership aan huidige user (BELANGRIJK FIX)
sudo chown -R "$USER_NAME":"$USER_NAME" "$APP_DIR"

cd "$APP_DIR"

echo "⬇️ Downloading project files..."
curl -fsSL "$REPO/server.py" -o server.py
curl -fsSL "$REPO/config.json" -o config.json
curl -fsSL "$REPO/version.txt" -o version.txt
curl -fsSL "$REPO/update.sh" -o update.sh

chmod +x update.sh

echo "🐍 Creating Python virtual environment..."
python3 -m venv zmanim-env

./zmanim-env/bin/pip install --upgrade pip
./zmanim-env/bin/pip install flask zmanim convertdate

echo "⚙️ Creating systemd service..."

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

echo "🔄 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "🧪 Testing API..."
sleep 3

if curl -fsS "http://localhost:5000/zmanim?date=$(date +%F)" >/dev/null; then
    echo "✅ Installation successful - API working"
else
    echo "❌ API test failed - check logs"
    echo "👉 journalctl -u $SERVICE_NAME -e"
    exit 1
fi

echo "🎉 Done!"
echo "👉 API: http://localhost:5000/zmanim"
