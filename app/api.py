from flask import Flask, jsonify
import json
import os
from app.zmanim import get_active_event

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# -------------------------
# SAFE CITY LOADER
# -------------------------
def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")

    # auto-create config if missing (CRITICAL FOR AUTO INSTALL)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"city": "antwerp"}, f)

    try:
        with open(path, "r") as f:
            return json.load(f).get("city", "antwerp")
    except:
        return "antwerp"


# -------------------------
# SAFE DATA PATH
# -------------------------
def get_data_path(city):
    path = os.path.join(BASE_DIR, "data", f"{city}.json")

    if not os.path.exists(path):
        return None

    return path


# -------------------------
# STATUS ENDPOINT
# -------------------------
@app.route("/status")
def status():
    city = get_city()
    path = get_data_path(city)

    event = None

    if path:
        try:
            event = get_active_event(path)
        except Exception as e:
            print("Zmanim error:", e)

    return jsonify({
        "city": city,
        "active": event is not None,
        "event": event
    })


# -------------------------
# ZMANIM ENDPOINT
# -------------------------
@app.route("/zmanim")
def zmanim():
    city = get_city()
    path = get_data_path(city)

    event = None

    if path:
        try:
            event = get_active_event(path)
        except Exception as e:
            print("Zmanim error:", e)

    return jsonify({
        "city": city,
        "active": event is not None,
        "event": event
    })


# -------------------------
# HEALTH CHECK (FOR SYSTEMD / MONITORING)
# -------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })
