#!/bin/bash

set -e

CITY=${1:-antwerp}
REPO="https://github.com/senmdaniel/zmanim-pro.git"
APP_DIR="$HOME/zmanim-pro"

echo "🚀 Zmanim-Pro Installer"
echo "🌍 City: $CITY"

# -------------------------
# 1. dependencies
# -------------------------
sudo apt update -y
sudo apt install -y git python3 python3-pip python3-venv

# -------------------------
# 2. clone repo
# -------------------------
if [ -d "$APP_DIR/.git" ]; then
    echo "🔄 Updating repo..."
    cd "$APP_DIR"
    git pull
else
    echo "⬇️ Cloning repo..."
    git clone "$REPO" "$APP_DIR"
    cd "$APP_DIR"
fi

# -------------------------
# 3. python venv (clean + safe)
# -------------------------
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# -------------------------
# 4. config (SAFE)
# -------------------------
mkdir -p config

cat > config/settings.json <<EOF
{
  "city": "$CITY"
}
EOF

# -------------------------
# 5. systemd service (NO sudo later needed)
# -------------------------
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Pro
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python app/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zmanim.service
sudo systemctl restart zmanim.service

# -------------------------
# 6. done
# -------------------------
echo "✅ INSTALL COMPLETE"
echo "🌐 http://$(hostname -I | awk '{print $1}'):5000/status"
