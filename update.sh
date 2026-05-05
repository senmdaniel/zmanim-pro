#!/bin/bash

APP_DIR="$HOME/zmanim-pro"

echo "🔄 Checking for updates..."

cd $APP_DIR || exit

# force correct repo state
git fetch origin

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⬇️ Update gevonden"

    git reset --hard origin/main

    # activate venv properly
    source "$APP_DIR/venv/bin/activate"

    pip install -r requirements.txt

    sudo systemctl restart zmanim.service

    echo "✅ Update toegepast"
else
    echo "✔ Geen updates"
fi
