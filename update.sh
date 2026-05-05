#!/bin/bash

APP_DIR="$HOME/zmanim-pro"

echo "🔄 Checking for updates..."

cd $APP_DIR || exit

git pull

source venv/bin/activate
pip install -r requirements.txt

sudo systemctl restart zmanim.service

echo "✅ Update complete"
