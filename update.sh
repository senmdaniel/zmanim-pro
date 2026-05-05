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
# prevent parallel runs
# -------------------------
if [ -f "$LOCK_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Update al bezig" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# -------------------------
# fetch latest code
# -------------------------
git fetch origin >> "$LOG_FILE" 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

# -------------------------
# no update
# -------------------------
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✔ Geen updates (versie: $LOCAL)" >> "$LOG_FILE"
    exit 0
fi

# -------------------------
# update found
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ⬇️ Update gevonden" >> "$LOG_FILE"
echo "   local : $LOCAL" >> "$LOG_FILE"
echo "   remote: $REMOTE" >> "$LOG_FILE"

git reset --hard origin/main >> "$LOG_FILE" 2>&1

echo "$REMOTE" > "$VERSION_FILE"

# -------------------------
# python deps
# -------------------------
source "$APP_DIR/venv/bin/activate"

pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# -------------------------
# SAFE restart (NO sudo needed)
# -------------------------
systemctl restart zmanim.service >> "$LOG_FILE" 2>&1

# -------------------------
# done
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Update voltooid" >> "$LOG_FILE"
echo "👉 Actieve versie: $REMOTE" >> "$LOG_FILE"
echo "--------------------------------------------------" >> "$LOG_FILE"
