from flask import Flask, jsonify, request
import json
import os
from app.zmanim import get_active_event

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


@app.route("/status")
def status():
    city = get_city()
    date = request.args.get("datum")

    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    path = os.path.join(BASE_DIR, "data", f"{city}.json")
    event = get_active_event(path)

    return jsonify({
        "city": city,
        "date": date,
        "holiday": event.get("holiday") if event else None,
        "type": event.get("type") if event else None,
        "is_yom_tov": event.get("type") == "yom_tov" if event else False,
        "plag_hamincha": event.get("plag_hamincha") if event else None,
        "tzeis": event.get("tzeis") if event else None
    })


@app.route("/zmanim")
def zmanim():
    return status()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})
