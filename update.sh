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
# 1. prevent double runs
# -------------------------
if [ -f "$LOCK_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Update al bezig - skip" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# -------------------------
# 2. fetch updates
# -------------------------
git fetch origin >> "$LOG_FILE" 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

# -------------------------
# 3. no updates
# -------------------------
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✔ Geen updates" >> "$LOG_FILE"
    exit 0
fi

# -------------------------
# 4. update found
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ⬇️ Update gevonden: $LOCAL → $REMOTE" >> "$LOG_FILE"

# backup version
echo "$LOCAL" > "$APP_DIR/.last_version"

# hard reset repo
git reset --hard origin/main >> "$LOG_FILE" 2>&1

# version file (commit hash)
echo "$REMOTE" > "$VERSION_FILE"

# -------------------------
# 5. python environment
# -------------------------
source "$APP_DIR/venv/bin/activate"

pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# -------------------------
# 6. restart service (NO SUDO FIX)
# -------------------------
systemctl restart zmanim.service >> "$LOG_FILE" 2>&1

# -------------------------
# 7. done
# -------------------------
echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Update succesvol + service herstart" >> "$LOG_FILE"
