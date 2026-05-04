#!/bin/bash

set -e

echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installing Python + pip..."
sudo apt install -y python3 python3-pip git

echo "📁 Cloning repo..."
cd /home/pi
if [ -d "loxone-zmanim-pi" ]; then
  echo "Repo bestaat al, updaten..."
  cd loxone-zmanim-pi
  git pull
else
  git clone https://github.com/JOUWNAAM/loxone-zmanim-pi.git
  cd loxone-zmanim-pi
fi

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "⚙️ Installing systemd service..."
sudo cp systemd/zmanim.service /etc/systemd/system/zmanim.service

echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ Installation complete!"
echo "🌐 API running at: http://<pi-ip>:5000/zmanim"
