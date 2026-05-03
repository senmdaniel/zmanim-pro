#!/bin/bash

echo "🚀 Installing Zmanim PRO..."

# update systeem
sudo apt update -y

# python + venv
sudo apt install -y python3 python3-venv python3-pip

# map maken
mkdir -p /home/mjd/zmanim-pro
cd /home/mjd/zmanim-pro

# virtual env
python3 -m venv zmanim-env
source zmanim-env/bin/activate

# libraries
pip install flask zmanim convertdate

# server downloaden (later vervangen door jouw github)
cp server.py /home/mjd/zmanim-pro/server.py

# config
cat > /home/mjd/zmanim-pro/config.json <<EOF
{
  "city": "antwerp"
}
EOF

# systemd service
sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Flask Server
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

# reload + start
sudo systemctl daemon-reload
sudo systemctl enable zmanim
sudo systemctl restart zmanim

echo "✅ Installation complete!"
"   mjd@mjd:~/zmanim-pro $
