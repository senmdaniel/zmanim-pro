#!/bin/bash

set -e

APP_DIR="$HOME/zmanim-pro"
LOG_FILE="$APP_DIR/update.log"
VERSION_FILE="$APP_DIR/version.txt"
LOCK_FILE="$APP_DIR/update.lock"

echo "--------------------------------------------------" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 🔄 Update check gestart" >> "$LOG_FILE"

cd "$APP_DIR" || exit 1

# -------------------------
# 1. prevent double run
# -------------------------
if [ -f "$LOCK_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Update al bezig - skip" >> "$LOG_FILE"
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
# 3. no update
# -------------------------
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✔ Geen updates (versie: $LOCAL)" >> "$LOG_FILE"
    exit 0
fi

# -------------------------
# 4. update found
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ⬇️ Update gevonden" >> "$LOG_FILE"
echo "   huidige versie: $LOCAL" >> "$LOG_FILE"
echo "   nieuwe versie : $REMOTE" >> "$LOG_FILE"

# backup version
echo "$LOCAL" > "$APP_DIR/.last_version"

# apply update
git reset --hard origin/main >> "$LOG_FILE" 2>&1

# store new version
echo "$REMOTE" > "$VERSION_FILE"

# -------------------------
# 5. python deps
# -------------------------
source "$APP_DIR/venv/bin/activate"

pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# -------------------------
# 6. restart service
# -------------------------
systemctl restart zmanim.service >> "$LOG_FILE" 2>&1

# -------------------------
# 7. FINAL OUTPUT (BELANGRIJK)
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Update voltooid" >> "$LOG_FILE"
echo "👉 Actieve versie: $REMOTE" >> "$LOG_FILE"

echo "--------------------------------------------------" >> "$LOG_FILE"
