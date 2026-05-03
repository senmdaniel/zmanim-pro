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

echo "⬆️ Update available - downloading safely..."

TMP_DIR="/tmp/zmanim_update"
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

# download to temp first (IMPORTANT FIX)
curl -fsSL "$REPO/server.py" -o "$TMP_DIR/server.py"
curl -fsSL "$REPO/config.json" -o "$TMP_DIR/config.json"
curl -fsSL "$REPO/version.txt" -o "$TMP_DIR/version.txt"

# validate downloads
if [ ! -s "$TMP_DIR/server.py" ]; then
    echo "❌ Download failed - aborting update"
    exit 1
fi

echo "📦 Applying update..."

cp "$TMP_DIR/server.py" "$APP_DIR/server.py"
cp "$TMP_DIR/config.json" "$APP_DIR/config.json"
cp "$TMP_DIR/version.txt" "$APP_DIR/version.txt"

echo "🔄 Restarting service..."
sudo systemctl restart zmanim

sleep 2

if systemctl is-active --quiet zmanim; then
    echo "✅ Update successful to $REMOTE"
else
    echo "❌ Service failed after update - rolling back not implemented yet"
    exit 1
fi
