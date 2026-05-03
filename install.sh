#!/bin/bash

APP=/opt/zmanim
REPO=https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main

sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl

sudo rm -rf $APP
sudo mkdir -p $APP
sudo chown -R mjd:mjd $APP
cd $APP

curl -fsSL $REPO/server.py -o server.py
curl -fsSL $REPO/yom_tov.py -o yom_tov.py
curl -fsSL $REPO/requirements.txt -o requirements.txt
curl -fsSL $REPO/version.txt -o version.txt

python3 -m venv venv
./venv/bin/pip install -r requirements.txt

echo "[Unit]
Description=Zmanim
After=network.target

[Service]
User=mjd
WorkingDirectory=/opt/zmanim
ExecStart=/opt/zmanim/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/zmanim.service

sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim
