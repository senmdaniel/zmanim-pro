#!/bin/bash

set -e

CITY=${1:-antwerp}
REPO="https://github.com/senmdaniel/zmanim-pro.git"
APP_DIR="$HOME/zmanim-pro"

echo "🚀 Zmanim-Pro PRO Installer"
echo "🌍 City: $CITY"

# -------------------------
# 1. system dependencies
# -------------------------
sudo apt update -y
sudo apt install -y git python3 python3-venv python3-pip

# -------------------------
# 2. clone or update
# -------------------------
if [ -d "$APP_DIR/.git" ]; then
    echo "🔄 Updating repo..."
    cd $APP_DIR
    git fetch origin
    git reset --hard origin/main
else
    echo "⬇️ Cloning repo..."
    git clone $REPO $APP_DIR
    cd $APP_DIR
fi

# -------------------------
# 3. python venv setup
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
# 5. update script (AUTO UPDATE)
# -------------------------
cat > $APP_DIR/update.sh << 'EOF'
#!/bin/bash

APP_DIR="$HOME/zmanim-pro"

echo "🔄 Checking for updates..."

cd $APP_DIR || exit

git fetch origin

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⬇️ Update gevonden"

    git reset --hard origin/main

    source "$APP_DIR/venv/bin/activate"
    pip install -r requirements.txt

    sudo systemctl restart zmanim.service

    echo "✅ Update toegepast"
else
    echo "✔ Geen updates"
fi
EOF

chmod +x $APP_DIR/update.sh

# -------------------------
# 6. cron job (auto updates)
# -------------------------
(crontab -l 2>/dev/null | grep -v "zmanim-pro/update.sh"; echo "*/10 * * * * bash $APP_DIR/update.sh >> $APP_DIR/update.log 2>&1") | crontab -

# -------------------------
# 7. systemd service
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
# 8. start service
# -------------------------
sudo systemctl daemon-reload
sudo systemctl enable zmanim.service
sudo systemctl restart zmanim.service

# -------------------------
# DONE
# -------------------------
IP=$(hostname -I | awk '{print $1}')

echo "✅ INSTALL COMPLETE"
echo "🌐 http://$IP:5000/status"
echo "🔄 Auto-updates actief (elke 10 min)"
