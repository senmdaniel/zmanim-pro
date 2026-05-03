#!/bin/bash

APP=/opt/zmanim
REPO=https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main
SERVICE=zmanim

cd $APP

LOCAL=$(cat version.txt)
REMOTE=$(curl -fsSL $REPO/version.txt)

echo "Local: $LOCAL"
echo "Remote: $REMOTE"

[ "$LOCAL" = "$REMOTE" ] && echo "Up to date" && exit 0

sudo systemctl stop $SERVICE

curl -fsSL $REPO/server.py -o server.py
curl -fsSL $REPO/yom_tov.py -o yom_tov.py
echo "$REMOTE" > version.txt

rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

sudo systemctl restart $SERVICE

echo "Updated to $REMOTE"
