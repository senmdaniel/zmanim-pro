#!/bin/bash

set -e  # stop bij errors

CITY=${1:-antwerp}
REPO="https://github.com/JOUWNAAM/zmanim-pro.git"
DIR="/home/pi/zmanim-pro"

echo "===================================="
echo "📦 Zmanim-Pro Installer"
echo "🌍 City: $CITY"
echo "===================================="

# ----------------------------
# 1. System dependencies
# ----------------------------
echo "🔧 Installing system dependencies..."
sudo apt update -y
sudo apt install -y git python3 python3-pip

# ----------------------------
# 2. Clone or update repo
# ----------------------------
if [ -d "$DIR/.git" ]; then
    echo "🔄 Existing install found → updating..."
    cd $DIR
    git pull origin main
else
    echo "⬇️ Fresh install → cloning repo..."
    git clone $REPO $DIR
    cd $DIR
fi

# ----------------------------
# 3. Python dependencies
# ----------------------------
echo "🐍 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# ----------------------------
# 4. Config setup
# ----------------------------
echo "⚙️ Creating configuration..."

mkdir -p config

cat > config/settings.json <<EOF
{
  "city": "$CITY"
}
EOF

echo "📍 Config set to: $CITY"

# ----------------------------
# 5. Test run (safe)
# ----------------------------
echo "🧪 Testing application..."

timeout 5s python3 app/main.py || echo "⚠️ App test skipped (normal on first run)"

# ----------------------------
# 6. Create simple launcher script
# ----------------------------
cat > start.sh <<EOF
#!/bin/bash
cd $DIR
python3 app/main.py
EOF

chmod +x start.sh

# ----------------------------
# 7. Optional: systemd service (AUTO START)
# ----------------------------
echo "⚙️ Setting up auto-start service..."

sudo tee /etc/systemd/system/zmanim.service > /dev/null <<EOF
[Unit]
Description=Zmanim Pro Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $DIR/app/main.py
WorkingDirectory=$DIR
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zmanim.service
sudo systemctl restart zmanim.service

# ----------------------------
# DONE
# ----------------------------
echo "===================================="
echo "✅ INSTALL COMPLETE"
echo "🌐 API: http://localhost:5000/status"
echo "🔁 Auto-start: ENABLED"
echo "📁 Path: $DIR"
echo "===================================="
