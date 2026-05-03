#!/bin/bash

set -euo pipefail

REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

echo "🚀 Zmanim PRO bootstrap installer"

echo "⬇️ Downloading installer..."

curl -fsSL "$REPO/install.sh" -o install.sh

if [ ! -f install.sh ]; then
  echo "❌ Download failed"
  exit 1
fi

echo "🔐 Running installer..."

bash install.sh
