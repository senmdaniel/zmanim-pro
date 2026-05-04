from flask import Flask, jsonify
import json
import os
from app.zmanim import get_active_event

app = Flask(__name__)

# absolute base path (BELANGRIJK voor Pi + systemd + GitHub installs)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


@app.route("/status")
def status():
    city = get_city()

    path = os.path.join(BASE_DIR, "data", f"{city}.json")
    event = get_active_event(path)

    return jsonify({
        "city": city,
        "active": event is not None,
        "event": event
    })


@app.route("/zmanim")
def zmanim():
    city = get_city()

    path = os.path.join(BASE_DIR, "data", f"{city}.json")
    event = get_active_event(path)

    return jsonify({
        "city": city,
        "active": event is not None,
        "event": event
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})
