#!/bin/bash

set -e

echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installing system packages..."
sudo apt install -y python3 python3-pip python3-venv git

PROJECT="/home/mjd/zmanim-pro"

echo "📁 Cloning/updating project..."
if [ -d "$PROJECT" ]; then
  cd $PROJECT
  git pull
else
  git clone https://github.com/senmdaniel/zmanim-pro.git $PROJECT
  cd $PROJECT
fi

echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install flask astral

echo "⚙️ Creating systemd service..."

sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim API
After=network.target

[Service]
WorkingDirectory=/home/mjd/zmanim-pro
ExecStart=/home/mjd/zmanim-pro/venv/bin/python app.py
Restart=always
User=mjd

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ INSTALL COMPLETE"
echo "🌐 http://$(hostname -I | awk '{print $1}'):5000/zmanim"
