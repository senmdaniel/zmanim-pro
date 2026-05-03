#!/bin/bash
set -euo pipefail

echo "🚀 Installing Zmanim PRO"

APP="/opt/zmanim"
REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

sudo mkdir -p $APP
sudo chown -R mjd:mjd $APP
cd $APP

curl -fsSL $REPO/server.py -o server.py
curl -fsSL $REPO/yom_tov.py -o yom_tov.py
curl -fsSL $REPO/requirements.txt -o requirements.txt
curl -fsSL $REPO/version.txt -o version.txt
curl -fsSL $REPO/update.sh -o update.sh

chmod +x update.sh

python3 -m venv zmanim-env
./zmanim-env/bin/pip install --upgrade pip
./zmanim-env/bin/pip install -r requirements.txt

sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim PRO
After=network.target

[Service]
User=mjd
WorkingDirectory=/opt/zmanim
ExecStart=/opt/zmanim/zmanim-env/bin/python /opt/zmanim/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ INSTALL COMPLETE"
