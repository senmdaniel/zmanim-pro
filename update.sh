#!/bin/bash

set -e

APP_DIR="$HOME/zmanim-pro"
LOG_FILE="$APP_DIR/update.log"
LOCK_FILE="$APP_DIR/update.lock"
VERSION_FILE="$APP_DIR/version.txt"

echo "--------------------------------------------------" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 🔄 Update check gestart" >> "$LOG_FILE"

cd "$APP_DIR" || exit 1

# -------------------------
# lock
# -------------------------
if [ -f "$LOCK_FILE" ]; then
    echo "⚠️ Update al bezig" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# -------------------------
# fetch
# -------------------------
git fetch origin >> "$LOG_FILE" 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✔ Geen updates (versie: $LOCAL)" >> "$LOG_FILE"
    exit 0
fi

echo "⬇️ Update gevonden" >> "$LOG_FILE"
echo "Local : $LOCAL" >> "$LOG_FILE"
echo "Remote: $REMOTE" >> "$LOG_FILE"

# -------------------------
# update
# -------------------------
git reset --hard origin/main >> "$LOG_FILE" 2>&1

echo "$REMOTE" > "$VERSION_FILE"

# -------------------------
# python env
# -------------------------
source "$APP_DIR/venv/bin/activate"
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# -------------------------
# SAFE restart (NO sudo)
# -------------------------
if systemctl is-active --quiet zmanim.service; then
    systemctl restart zmanim.service >> "$LOG_FILE" 2>&1
    echo "🔁 Service restarted" >> "$LOG_FILE"
else
    echo "⚠️ Service not active, start instead" >> "$LOG_FILE"
    systemctl start zmanim.service >> "$LOG_FILE" 2>&1
fi

# -------------------------
# success ONLY if everything ok
# -------------------------
if systemctl is-active --quiet zmanim.service; then
    echo "✅ Update succesvol + service draait" >> "$LOG_FILE"
    echo "👉 Actieve versie: $REMOTE" >> "$LOG_FILE"
else
    echo "❌ UPDATE MISLUKT - service draait niet" >> "$LOG_FILE"
    exit 1
fi

echo "--------------------------------------------------" >> "$LOG_FILE"
