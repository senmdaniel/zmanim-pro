import os
import sys
import subprocess
import json

CITY = sys.argv[1] if len(sys.argv) > 1 else "antwerp"

REPO_URL = "https://github.com/JOUWNAAM/zmanim-pro.git"
BASE_DIR = f"/home/pi/zmanim-pro"

print("📦 Installing Zmanim-Pro...")

# 1. Clone repo
if not os.path.exists(BASE_DIR):
    subprocess.run(["git", "clone", REPO_URL, BASE_DIR])

# 2. Set city config
config = {
    "city": CITY
}

os.makedirs(f"{BASE_DIR}/config", exist_ok=True)

with open(f"{BASE_DIR}/config/settings.json", "w") as f:
    json.dump(config, f)

# 3. Install dependencies
subprocess.run(["pip3", "install", "-r", f"{BASE_DIR}/requirements.txt"])

print("✅ Installed for city:", CITY)
print("🚀 Run: python3 app/main.py")
