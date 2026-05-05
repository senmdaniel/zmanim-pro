from flask import Flask, jsonify, request
from datetime import date, datetime
import json
import os

from app.zmanim import calculate_zmanim, get_holiday_info

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------
# CONFIG
# ---------------------------
def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


# ---------------------------
# DATE PARSER (SINGLE SOURCE OF TRUTH)
# ---------------------------
def parse_date():
    """
    Enige toegestane input:
    - ?date=2026-05-05
    - ?date=2026/05/05
    - ?datum=2026-05-05
    - ?datum=2026/05/05

    Regel:
    - URL = waarheid
    - geen stille overrides
    """

    raw = request.args.get("date") or request.args.get("datum")

    # Geen datum → expliciet vandaag + warning
    if not raw:
        return date.today(), "missing_date_used_today"

    raw_clean = raw.replace("/", "-")

    try:
        parsed = datetime.strptime(raw_clean, "%Y-%m-%d").date()
        return parsed, None
    except ValueError:
        return None, f"invalid_date_format:{raw}"


# ---------------------------
# STATUS ENDPOINT
# ---------------------------
@app.route("/status")
def status():
    city = get_city()
    d, warning = parse_date()

    if d is None:
        return jsonify({
            "error": warning
        }), 400

    zmanim = calculate_zmanim(city, d)
    holiday = get_holiday_info(city, d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        "warning": warning,
        "is_yom_tov": holiday.get("is_yom_tov"),
        "holiday": holiday.get("name"),
        **zmanim
    })


# ---------------------------
# ZMANIM ENDPOINT
# ---------------------------
@app.route("/zmanim")
def zmanim_route():
    city = get_city()
    d, warning = parse_date()

    if d is None:
        return jsonify({
            "error": warning
        }), 400

    zmanim = calculate_zmanim(city, d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        "warning": warning,
        **zmanim
    })


# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


# ---------------------------
# ENTRYPOINT
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
