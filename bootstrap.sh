#!/bin/bash

echo "🚀 Zmanim PRO bootstrap installer"

MODE="${1:-normal}"

REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

echo "⬇️ Downloading installer..."
curl -fsSL "$REPO/install.sh" -o /tmp/install.sh

chmod +x /tmp/install.sh

if [ "$MODE" = "clean" ]; then
  echo "🧹 CLEAN MODE ACTIVE"

  sudo systemctl stop zmanim 2>/dev/null || true
  sudo systemctl disable zmanim 2>/dev/null || true

  sudo rm -f /etc/systemd/system/zmanim.service
  sudo systemctl daemon-reload

  sudo rm -rf /opt/zmanim
  sudo rm -rf /home/mjd/zmanim-pro

  sudo pkill -f server.py || true
  sudo pkill -f zmanim || true

  echo "✅ Cleanup done"
fi

echo "🔐 Running installer..."
bash /tmp/install.sh
