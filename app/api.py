from flask import Flask, jsonify, request
from datetime import datetime, date
import json
import os

from app.zmanim import calculate_zmanim, get_holiday_info, get_hebrew_date

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORED_DATE_PATH = os.path.join(BASE_DIR, "config", "current_date.json")


def save_date(d):
    with open(STORED_DATE_PATH, "w") as f:
        json.dump({"date": d.isoformat()}, f)


def load_date():
    if not os.path.exists(STORED_DATE_PATH):
        return None
    try:
        with open(STORED_DATE_PATH, "r") as f:
            return datetime.strptime(json.load(f)["date"], "%Y-%m-%d").date()
    except:
        return None


def get_city():
    with open(os.path.join(BASE_DIR, "config", "settings.json")) as f:
        return json.load(f)["city"]


def get_config(city):
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path) as f:
        cfg = json.load(f)
    cfg["city"] = city
    return cfg


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api")
def api():
    raw = request.args.get("d") or request.args.get("date")

    if raw:
        try:
            d = datetime.strptime(raw, "%Y%m%d").date() if "-" not in raw else datetime.strptime(raw, "%Y-%m-%d").date()
            save_date(d)
        except:
            return jsonify({"error": "invalid date"}), 400

    d = load_date()

    if not d:
        return jsonify({"error": "no date set"}), 400

    city = get_city()
    config = get_config(city)

    zmanim = calculate_zmanim(config, d)
    holiday = get_holiday_info(d)
    hebrew = get_hebrew_date(d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        "hebrew_date": hebrew["hebrew_date"],
        "holiday": holiday.get("holiday_name"),
        **zmanim
    })
