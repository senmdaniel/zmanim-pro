#!/bin/bash
set -euo pipefail

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"
SERVICE="zmanim"

echo "🔄 Checking updates..."

LOCAL=$(cat $APP_DIR/version.txt 2>/dev/null || echo "0.0.0")
REMOTE=$(curl -fsSL $REPO/version.txt)

echo "Local:  $LOCAL"
echo "Remote: $REMOTE"

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "✔ Already up to date"
  exit 0
fi

echo "⬆️ Update available"

sudo systemctl stop $SERVICE

BACKUP="/opt/zmanim_backup/$LOCAL"
sudo mkdir -p "$BACKUP"
sudo cp -r $APP_DIR "$BACKUP" || true

echo "💾 Backup created at $BACKUP"

cd $APP_DIR

# 🔥 CLEAN REBUILD (BELANGRIJK)
rm -rf zmanim-env
python3 -m venv zmanim-env

./zmanim-env/bin/pip install --upgrade pip
./zmanim-env/bin/pip install -r requirements.txt

# 🔄 FETCH LATEST CODE
curl -fsSL $REPO/server.py -o server.py
curl -fsSL $REPO/yom_tov.py -o yom_tov.py
curl -fsSL $REPO/requirements.txt -o requirements.txt

echo "$REMOTE" > version.txt

sudo systemctl daemon-reload
sudo systemctl restart $SERVICE

echo "✅ Updated to $REMOTE"
