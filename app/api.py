from flask import Flask, jsonify, request
from datetime import date, datetime
import json
import os

from app.zmanim import calculate_zmanim, get_holiday_info

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


def parse_date():
    """Loxone stuurt: ?date=2026-05-05 of 2026/05/05"""
    d = request.args.get("date")

    if not d:
        return date.today()

    d = d.replace("/", "-")
    return datetime.strptime(d, "%Y-%m-%d").date()


@app.route("/status")
def status():
    city = get_city()
    d = parse_date()

    zmanim = calculate_zmanim(city, d)
    holiday = get_holiday_info(city, d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        "is_yom_tov": holiday["is_yom_tov"],
        "holiday": holiday["name"],
        **zmanim
    })


@app.route("/zmanim")
def zmanim_route():
    city = get_city()
    d = parse_date()

    zmanim = calculate_zmanim(city, d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        **zmanim
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})
