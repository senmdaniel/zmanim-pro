#!/bin/bash
set -e

echo "🚀 Zmanim PRO installer v1..."

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

echo "📁 Creating app directory..."
sudo mkdir -p $APP_DIR
cd $APP_DIR

echo "⬇️ Downloading files..."
sudo curl -fsSL "$REPO/server.py" -o server.py
sudo curl -fsSL "$REPO/config.json" -o config.json
sudo curl -fsSL "$REPO/version.txt" -o version.txt
sudo curl -fsSL "$REPO/update.sh" -o update.sh

sudo chmod +x update.sh

echo "🐍 Setting up Python environment..."
python3 -m venv zmanim-env
./zmanim-env/bin/pip install --upgrade pip
./zmanim-env/bin/pip install flask zmanim convertdate

echo "⚙️ Creating systemd service..."

sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim PRO
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/zmanim-env/bin/python $APP_DIR/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ Installation complete!"
echo "👉 Running on: http://localhost:5000"
