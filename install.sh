#!/bin/bash
set -e

# ===== CONFIG =====
APP_DIR="$HOME/zmanim-pro"
SERVICE_NAME="zmanim"
GITHUB_REPO="https://github.com/senmdaniel/zmanim-pro.git"

echo "🚀 Zmanim-Pro installer starting..."
echo "📂 App directory: $APP_DIR"
echo "🌍 Cloning repo from: $GITHUB_REPO"

# Install dependencies
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip

# Clone repo if not exists
if [ ! -d "$APP_DIR" ]; then
    git clone "$GITHUB_REPO" "$APP_DIR"
fi

cd "$APP_DIR"

# Create virtualenv
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# ===== SYSTEMD SERVICE =====
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOL
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
EOL

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME.service"
sudo systemctl start "$SERVICE_NAME.service"

# ===== POLKIT RULE =====
POLKIT_FILE="/etc/polkit-1/rules.d/10-zmanim.rules"

sudo tee "$POLKIT_FILE" > /dev/null <<EOL
polkit.addRule(function(action, subject) {
    if (
        action.id == "org.freedesktop.systemd1.manage-units" &&
        subject.user == "$USER"
    ) {
        return polkit.Result.YES;
    }
});
EOL

# ===== UPDATE SCRIPT =====
UPDATE_SCRIPT="$APP_DIR/update.sh"

tee "$UPDATE_SCRIPT" > /dev/null <<'EOF'
#!/bin/bash
set -e

APP_DIR="$HOME/zmanim-pro"
LOG_FILE="$APP_DIR/update.log"
VERSION_FILE="$APP_DIR/version.txt"

echo "--------------------------------------------------" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 🔄 Update check gestart" >> "$LOG_FILE"

cd "$APP_DIR" || exit 1

git fetch origin >> "$LOG_FILE" 2>&1
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✔ Geen updates (versie: $LOCAL)" >> "$LOG_FILE"
    exit 0
fi

echo "⬇️ Update gevonden: $LOCAL → $REMOTE" >> "$LOG_FILE"

git reset --hard origin/main >> "$LOG_FILE" 2>&1
echo "$REMOTE" > "$VERSION_FILE"

source "$APP_DIR/venv/bin/activate"
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

systemctl restart zmanim.service >> "$LOG_FILE" 2>&1
echo "✅ Update succesvol + service draait (versie: $REMOTE)" >> "$LOG_FILE"
echo "--------------------------------------------------" >> "$LOG_FILE"
EOF

chmod +x "$UPDATE_SCRIPT"

# ===== CRON JOB =====
(crontab -l 2>/dev/null; echo "*/10 * * * * $UPDATE_SCRIPT") | crontab -

echo "✅ Installation complete!"
echo "🌐 Zmanim status: http://$(hostname -I | awk '{print $1}'):5000/status"
