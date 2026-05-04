#!/bin/bash

set -e

CITY=${1:-antwerp}
DIR="$HOME/zmanim-pro"
REPO="https://github.com/senmdaniel/zmanim-pro.git"

echo "🚀 Installing Zmanim-Pro for $CITY"

sudo apt update -y
sudo apt install -y git python3 python3-pip

if [ -d "$DIR/.git" ]; then
    cd $DIR
    git pull
else
    git clone $REPO $DIR
    cd $DIR
fi

pip3 install -r requirements.txt

mkdir -p config

echo "{\"city\": \"$CITY\"}" > config/settings.json

echo "⚙️ Setup complete"

# optional service
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Pro
After=network.target

[Service]
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 app/main.py
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zmanim.service
sudo systemctl restart zmanim.service

echo "✅ DONE"
echo "🌐 http://localhost:5000/status"
