from flask import Flask, jsonify
from zmanim import get_active_event
import json

app = Flask(__name__)

# -----------------------------
# Load city from config
# -----------------------------
def get_city():
    with open("config/settings.json", "r") as f:
        return json.load(f)["city"]

# -----------------------------
# API: status endpoint (for Loxone)
# -----------------------------
@app.route("/status")
def status():
    city = get_city()

    # laad juiste city JSON
    event = get_active_event(f"data/{city}.json")

    return jsonify({
        "city": city,
        "active": event is not None,
        "event": event
    })

# -----------------------------
# Optional: health check
# -----------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })
