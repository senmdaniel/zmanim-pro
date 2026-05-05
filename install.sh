#!/bin/bash

set -e

CITY=${1:-antwerp}
REPO="https://github.com/senmdaniel/zmanim-pro.git"
APP_DIR="$HOME/zmanim-pro"

echo "🚀 Zmanim-Pro PRO Installer"
echo "🌍 City: $CITY"

# -------------------------
# 1. system deps
# -------------------------
sudo apt update -y
sudo apt install -y git python3 python3-venv python3-pip

# -------------------------
# 2. clone/update
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
# 3. venv setup
# -------------------------
cd $APP_DIR

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# -------------------------
# 4. config
# -------------------------
mkdir -p config

echo "{\"city\": \"$CITY\"}" > config/settings.json

# -------------------------
# 5. systemd (FIXED IMPORT ISSUE)
# -------------------------
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Pro
After=network.target

[Service]
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python -m app.main
Restart=always
RestartSec=3
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# -------------------------
# 6. start service
# -------------------------
sudo systemctl daemon-reload
sudo systemctl enable zmanim.service
sudo systemctl restart zmanim.service

echo "✅ INSTALL COMPLETE"
echo "🌐 http://$(hostname -I | awk '{print $1}'):5000/status"
