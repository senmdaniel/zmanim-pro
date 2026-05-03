#!/bin/bash
set -euo pipefail

APP_DIR="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

echo "🔄 Checking updates..."

LOCAL=$(cat "$APP_DIR/version.txt" 2>/dev/null || echo "0.0.0")
REMOTE=$(curl -fsSL "$REPO/version.txt" || echo "0.0.0")

echo "Local:  $LOCAL"
echo "Remote: $REMOTE"

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✔ Already up to date"
    exit 0
fi

echo "⬆️ Update available"

# 🧯 BACKUP (IMPORTANT)
BACKUP_DIR="/opt/zmanim_backup/$LOCAL"
mkdir -p "$BACKUP_DIR"

cp -r "$APP_DIR"/* "$BACKUP_DIR/"

echo "💾 Backup created at $BACKUP_DIR"

# 📦 TEMP DOWNLOAD
TMP="/tmp/zmanim_update"
rm -rf "$TMP"
mkdir -p "$TMP"

curl -fsSL "$REPO/server.py" -o "$TMP/server.py"
curl -fsSL "$REPO/config.json" -o "$TMP/config.json"
curl -fsSL "$REPO/version.txt" -o "$TMP/version.txt"

# 🧪 VALIDATE
if [ ! -s "$TMP/server.py" ]; then
    echo "❌ Download failed"
    exit 1
fi

# 🚀 APPLY UPDATE
cp "$TMP/server.py" "$APP_DIR/server.py"
cp "$TMP/config.json" "$APP_DIR/config.json"
cp "$TMP/version.txt" "$APP_DIR/version.txt"

echo "🔄 Restarting service..."
sudo systemctl restart zmanim

sleep 2

if systemctl is-active --quiet zmanim; then
    echo "✅ Updated to $REMOTE"
else
    echo "❌ Update failed → rolling back"

    cp -r "$BACKUP_DIR"/* "$APP_DIR/"

    sudo systemctl restart zmanim

    echo "🔁 Rollback completed"
fi
