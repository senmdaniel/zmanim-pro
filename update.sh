#!/bin/bash

REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

cd /home/mjd/zmanim-pro

echo "🔄 Checking updates..."

LOCAL=$(cat version.txt)
REMOTE=$(curl -s $REPO/version.txt)

echo "Local: $LOCAL"
echo "Remote: $REMOTE"

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⬆️ Updating Zmanim PRO..."

    curl -O $REPO/server.py
    curl -O $REPO/version.txt

    sudo systemctl restart zmanim

    echo "✅ Updated to $REMOTE"
else
    echo "✔ Already up to date"
fi
