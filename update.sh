#!/bin/bash

APP_DIR="/opt/zmanim"
REPO_DIR="/opt/zmanim"
BACKUP_DIR="/opt/zmanim_backup"
VENV="$APP_DIR/zmanim-env"
VERSION_FILE="$APP_DIR/version.txt"

echo "🔄 Checking updates..."

cd $REPO_DIR || exit 1

LOCAL=$(cat version.txt)
REMOTE=$(curl -s https://raw.githubusercontent.com/YOUR_GITHUB_USER/zmanim_calendar/main/version.txt)

echo "Local:  $LOCAL"
echo "Remote: $REMOTE"

if [ "$LOCAL" == "$REMOTE" ]; then
    echo "✔ Already up to date"
    exit 0
fi

echo "⬆️ Update available"

# -----------------------
# BACKUP (NO ROOT REQUIRED)
# -----------------------
mkdir -p "$BACKUP_DIR"
cp -r "$APP_DIR" "$BACKUP_DIR/$LOCAL"

echo "💾 Backup created at $BACKUP_DIR/$LOCAL"

# -----------------------
# PULL FROM GIT
# -----------------------
cd $APP_DIR || exit 1

git reset --hard
git pull origin main

# -----------------------
# FIX PERMISSIONS
# -----------------------
chown -R mjd:mjd $APP_DIR

# -----------------------
# INSTALL REQUIREMENTS IN VENV
# -----------------------
source $VENV/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

deactivate

# -----------------------
# FIX COMMON BREAKS
# -----------------------

# remove broken leftover files
rm -f $APP_DIR/yom_tov.py.broken 2>/dev/null

# ensure file exists
if [ ! -f "$APP_DIR/yom_tov.py" ]; then
    echo "⚠️ Missing yom_tov.py - restoring from repo"
    git checkout main -- yom_tov.py
fi

# -----------------------
# RESTART SERVICE
# -----------------------
echo "🔄 Restarting service..."
systemctl restart zmanim

echo "✅ Updated to $REMOTE"
