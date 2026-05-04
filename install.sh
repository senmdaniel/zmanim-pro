#!/bin/bash

set -e

REPO="https://github.com/senmdaniel/loxone-zmanim-pi.git"
DIR="/home/pi/loxone-zmanim-pi"

echo "📦 System update..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installing dependencies..."
sudo apt install -y python3 python3-pip git

echo "📁 Cloning repo..."
if [ -d "$DIR" ]; then
  echo "Repo bestaat al → update"
  cd $DIR
  git pull
else
  git clone $REPO $DIR
fi

cd $DIR

echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

echo "⚙️ Installing systemd service..."
sudo cp systemd/zmanim.service /etc/systemd/system/zmanim.service

echo "🔄 Reload systemd..."
sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ Installatie voltooid!"
echo "🌐 API beschikbaar op:"
echo "http://$(hostname -I | awk '{print $1}'):5000/zmanim"
