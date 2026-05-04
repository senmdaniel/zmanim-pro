#!/bin/bash

set -e

CITY=${1:-antwerp}
REPO="https://github.com/senmdaniel/zmanim-pro.git"
DIR="$HOME/zmanim-pro"

echo "🚀 Zmanim-Pro Auto Installer"
echo "🌍 City: $CITY"

# -------------------------
# 1. dependencies
# -------------------------
sudo apt update -y
sudo apt install -y git python3 python3-pip

# -------------------------
# 2. install or update
# -------------------------
if [ -d "$DIR/.git" ]; then
    echo "🔄 Updating existing install..."
    cd $DIR
    git pull
else
    echo "⬇️ Cloning project..."
    git clone $REPO $DIR
    cd $DIR
fi

# -------------------------
# 3. python deps
# -------------------------
pip3 install -r requirements.txt

# -------------------------
# 4. config
# -------------------------
mkdir -p config

echo "{\"city\": \"$CITY\"}" > config/settings.json

# -------------------------
# 5. systemd service
# -------------------------
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Pro
After=network.target

[Service]
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 app/main.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zmanim.service
sudo systemctl restart zmanim.service

# -------------------------
# DONE
# -------------------------
echo "✅ INSTALL COMPLETE"
echo "🌐 http://localhost:5000/status"
