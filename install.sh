#!/bin/bash

echo "🚀 Zmanim PRO installer v1..."

REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

mkdir -p /home/mjd/zmanim-pro
cd /home/mjd/zmanim-pro

# download files
curl -O $REPO/server.py
curl -O $REPO/config.json
curl -O $REPO/version.txt
curl -O $REPO/update.sh

# python env
python3 -m venv zmanim-env
source zmanim-env/bin/activate

pip install flask zmanim convertdate

# systemd service
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim PRO
After=network.target

[Service]
User=mjd
WorkingDirectory=/home/mjd/zmanim-pro
ExecStart=/home/mjd/zmanim-pro/zmanim-env/bin/python /home/mjd/zmanim-pro/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ Zmanim PRO installed!"
