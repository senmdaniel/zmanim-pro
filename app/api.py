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
    """
    Ondersteunt:
    - ?date=2026-05-05
    - ?datum=2026/05/05
    - ?datum=2026-05-05
    """

    raw = request.args.get("date") or request.args.get("datum")

    if not raw:
        return date.today(), None  # geen fout

    raw_clean = raw.replace("/", "-")

    try:
        parsed = datetime.strptime(raw_clean, "%Y-%m-%d").date()
        return parsed, None
    except ValueError:
        return None, f"Invalid date format: '{raw}'. Use YYYY-MM-DD or YYYY/MM/DD"


@app.route("/status")
def status():
    city = get_city()
    d, error = parse_date()

    if error:
        return jsonify({
            "error": error
        }), 400

    zmanim = calculate_zmanim(city, d)
    holiday = get_holiday_info(city, d)

    return jsonify({
        "city": city,
        "requested_date": request.args.get("date") or request.args.get("datum"),
        "date": d.isoformat(),
        "is_yom_tov": holiday["is_yom_tov"],
        "holiday": holiday["name"],
        **zmanim
    })


@app.route("/zmanim")
def zmanim_route():
    city = get_city()
    d, error = parse_date()

    if error:
        return jsonify({
            "error": error
        }), 400

    zmanim = calculate_zmanim(city, d)

    return jsonify({
        "city": city,
        "requested_date": request.args.get("date") or request.args.get("datum"),
        "date": d.isoformat(),
        **zmanim
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Handig voor debug lokaal
    app.run(host="0.0.0.0", port=5000)
