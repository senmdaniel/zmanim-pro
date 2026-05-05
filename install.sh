#!/bin/bash

set -e

CITY=${1:-antwerp}
REPO="https://github.com/senmdaniel/zmanim-pro.git"
APP_DIR="$HOME/zmanim-pro"

echo "🚀 Zmanim-Pro Bootstrap Installer"
echo "🌍 City: $CITY"

# -------------------------
# 1. dependencies
# -------------------------
sudo apt update -y
sudo apt install -y git python3 python3-pip

# -------------------------
# 2. clone or update
# -------------------------
if [ -d "$APP_DIR/.git" ]; then
    echo "🔄 Updating repo..."
    cd $APP_DIR
    git pull
else
    echo "⬇️ Cloning repo..."
    git clone $REPO $APP_DIR
    cd $APP_DIR
fi

# -------------------------
# 3. python deps
# -------------------------
pip3 install -r requirements.txt

# -------------------------
# 4. safe config init (BELANGRIJK)
# -------------------------
mkdir -p config

if [ ! -f config/settings.json ]; then
    echo "{\"city\": \"$CITY\"}" > config/settings.json
fi

# -------------------------
# 5. systemd service
# -------------------------
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Pro
After=network.target

[Service]
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 app/main.py
Restart=always
User=$USER

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
