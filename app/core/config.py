import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SETTINGS_FILE = os.path.join(BASE_DIR, "config", "settings.json")


def load_config():

    if not os.path.exists(SETTINGS_FILE):
        return {
            "city": "Brussels",
            "timezone": "Europe/Brussels",
            "latitude": 50.85,
            "longitude": 4.35,
            "minhag": "standard_18",
            "alos": 72
        }

    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)
