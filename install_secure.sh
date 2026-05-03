#!/bin/bash

set -e

REPO="https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main"

echo "📦 Downloading installer..."

curl -fsSL "$REPO/install.sh" -o install.sh
curl -fsSL "$REPO/install.sh.sha256" -o install.sh.sha256

echo "🔐 Verifying integrity..."

sha256sum -c install.sh.sha256

if [ $? -ne 0 ]; then
  echo "❌ Integrity check failed. Aborting."
  exit 1
fi

echo "✅ Verified. Running installer..."

bash install.sh
