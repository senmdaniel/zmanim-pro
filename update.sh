#!/bin/bash

set -e

APP_DIR="$HOME/zmanim-pro"
LOG_FILE="$APP_DIR/update.log"
VERSION_FILE="$APP_DIR/version.txt"
LOCK_FILE="$APP_DIR/update.lock"

echo "--------------------------------------------------" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 🔄 Checking for updates..." >> "$LOG_FILE"

cd "$APP_DIR" || exit 1

# -------------------------
# 1. prevent parallel runs
# -------------------------
if [ -f "$LOCK_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Update already running - skipped" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# -------------------------
# 2. fetch latest
# -------------------------
git fetch origin >> "$LOG_FILE" 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

# -------------------------
# 3. no update needed
# -------------------------
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✔ No updates" >> "$LOG_FILE"
    exit 0
fi

# -------------------------
# 4. update process
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ⬇️ Update found: $LOCAL → $REMOTE" >> "$LOG_FILE"

# backup current version
echo "$LOCAL" > "$APP_DIR/.last_version"

# hard reset to avoid conflicts
git reset --hard origin/main >> "$LOG_FILE" 2>&1

# store version
echo "$REMOTE" > "$VERSION_FILE"

# -------------------------
# 5. python environment
# -------------------------
source "$APP_DIR/venv/bin/activate"

pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# -------------------------
# 6. restart service
# -------------------------
sudo systemctl restart zmanim.service

echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Update complete + service restarted" >> "$LOG_FILE"
