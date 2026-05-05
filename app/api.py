from flask import Flask, jsonify, request
from datetime import date, datetime
import json
import os

from app.zmanim import (
    calculate_zmanim,
    get_holiday_info,
    get_hebrew_date
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# -----------------------
# CONFIG
# -----------------------
def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


# -----------------------
# DATE PARSER (single source of truth)
# -----------------------
def parse_date():
    """
    Input:
    - ?date=2026-05-05
    - ?date=2026/05/05
    - ?datum=2026-05-05
    - ?datum=2026/05/05
    """

    raw = request.args.get("date") or request.args.get("datum")

    if not raw:
        return date.today(), "missing_date_used_today"

    raw_clean = raw.replace("/", "-")

    try:
        return datetime.strptime(raw_clean, "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"invalid_date_format:{raw}"


# -----------------------
# STATUS ENDPOINT
# -----------------------
@app.route("/status")
def status():
    city = get_city()
    d, warning = parse_date()

    if d is None:
        return jsonify({"error": warning}), 400

    zmanim = calculate_zmanim(city, d)
    holiday = get_holiday_info(city, d)
    hebrew = get_hebrew_date(d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),

        # 🕎 Hebrew calendar
        "hebrew_date": hebrew["hebrew_date"],
        "hebrew_day": hebrew["hebrew_day"],
        "hebrew_month": hebrew["hebrew_month"],
        "hebrew_year": hebrew["hebrew_year"],

        # 🪵 warnings (important for Loxone debugging)
        "warning": warning,

        # 🕎 holiday info
        "is_yom_tov": holiday.get("is_yom_tov"),
        "holiday": holiday.get("name"),

        # 🌅 zmanim
        **zmanim
    })


# -----------------------
# ZMANIM ENDPOINT
# -----------------------
@app.route("/zmanim")
def zmanim_route():
    city = get_city()
    d, warning = parse_date()

    if d is None:
        return jsonify({"error": warning}), 400

    zmanim = calculate_zmanim(city, d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        "warning": warning,
        **zmanim
    })


# -----------------------
# HEALTH CHECK
# -----------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
