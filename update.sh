#!/bin/bash

cd /opt/zmanim || exit 1

echo "🔄 Pulling latest from GitHub..."
git reset --hard
git pull origin main

echo "📦 Installing dependencies..."
/opt/zmanim/zmanim-env/bin/pip install -r requirements.txt

echo "🔄 Restarting service..."
sudo systemctl restart zmanim

echo "✅ Update done from GitHub"
