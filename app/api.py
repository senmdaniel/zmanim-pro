from flask import Flask, jsonify, request
import json
import os
from app.zmanim import get_event

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


def is_yom_tov(holiday):
    yom_tov_list = [
        "Pesach",
        "Shavuot",
        "Sukkot",
        "Rosh Hashana",
        "Yom Kippur"
    ]
    return holiday in yom_tov_list


@app.route("/status")
def status():
    city = get_city()

    date = request.args.get("datum")
    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    path = os.path.join(BASE_DIR, "data", f"{city}.json")
    event = get_event(path, date)

    if not event:
        return jsonify({
            "city": city,
            "date": date,
            "holiday": None,
            "type": None,
            "is_yom_tov": False,
            "plag_hamincha": None,
            "tzeis": None
        })

    holiday = event.get("holiday")

    return jsonify({
        "city": city,
        "date": date,
        "holiday": holiday,
        "type": event.get("type"),
        "is_yom_tov": is_yom_tov(holiday),
        "plag_hamincha": event.get("plag_hamincha"),
        "tzeis": event.get("tzeis")
    })


@app.route("/zmanim")
def zmanim():
    return status()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})
