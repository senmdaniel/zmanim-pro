#!/bin/bash

set -e

APP_DIR="$HOME/zmanim-pro"
LOG_FILE="$APP_DIR/update.log"
LOCK_FILE="$APP_DIR/update.lock"
VERSION_FILE="$APP_DIR/version.txt"

echo "--------------------------------------------------" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 🔄 Update check gestart" >> "$LOG_FILE"

cd "$APP_DIR" || exit 1

# lock
if [ -f "$LOCK_FILE" ]; then
    echo "⚠️ Update al bezig" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# fetch
git fetch origin >> "$LOG_FILE" 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✔ Geen updates (versie: $LOCAL)" >> "$LOG_FILE"
    exit 0
fi

echo "⬇️ Update: $LOCAL → $REMOTE" >> "$LOG_FILE"

# update code
git reset --hard origin/main >> "$LOG_FILE" 2>&1

echo "$REMOTE" > "$VERSION_FILE"

# python deps
source "$APP_DIR/venv/bin/activate"
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# -------------------------
# SAFE RESTART (NO SUDO, NO PASSWORD)
# -------------------------
systemctl restart zmanim.service >> "$LOG_FILE" 2>&1 || {
    echo "❌ restart failed" >> "$LOG_FILE"
    exit 1
}

# verify
if systemctl is-active --quiet zmanim.service; then
    echo "✅ Update OK + service running" >> "$LOG_FILE"
else
    echo "❌ SERVICE NOT RUNNING" >> "$LOG_FILE"
    exit 1
fi

echo "--------------------------------------------------" >> "$LOG_FILE"
