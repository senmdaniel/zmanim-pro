from flask import Flask, jsonify, request
from datetime import datetime, date
import json
import os

from app.zmanim import (
    calculate_zmanim,
    get_holiday_info,
    get_hebrew_date
)

app = Flask(__name__)

# -----------------------
# PATHS
# -----------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORED_DATE_PATH = os.path.join(BASE_DIR, "config", "current_date.json")


# -----------------------
# CONFIG
# -----------------------
def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


def get_config(city):
    path = os.path.join(BASE_DIR, "config", "settings.json")

    with open(path, "r") as f:
        cfg = json.load(f)

    cfg["city"] = city
    return cfg


# -----------------------
# DATE STORAGE
# -----------------------
def save_date(d: date):
    with open(STORED_DATE_PATH, "w") as f:
        json.dump({"date": d.isoformat()}, f)


def load_date():
    if not os.path.exists(STORED_DATE_PATH):
        return None

    try:
        with open(STORED_DATE_PATH, "r") as f:
            data = json.load(f)
            return datetime.strptime(data["date"], "%Y-%m-%d").date()
    except:
        return None


def parse_date_from_request():
    raw = request.args.get("date") or request.args.get("datum")

    if not raw:
        return None, "no_date_in_request"

    raw_clean = raw.replace("/", "-")

    try:
        d = datetime.strptime(raw_clean, "%Y-%m-%d").date()
        save_date(d)
        return d, "date_from_request"
    except ValueError:
        return None, "invalid_date_format"


# -----------------------
# CORE STATUS LOGIC
# -----------------------
def build_response(d: date, warning: str):
    city = get_city()
    config = get_config(city)

    zmanim = calculate_zmanim(config, d)
    holiday = get_holiday_info(d)
    hebrew = get_hebrew_date(d)

    return {
        "city": city,
        "date": d.isoformat(),
        "warning": warning,

        # Hebrew
        "hebrew_date": hebrew["hebrew_date"],
        "hebrew_day": hebrew["hebrew_day"],
        "hebrew_month": hebrew["hebrew_month"],
        "hebrew_year": hebrew["hebrew_year"],

        # Holiday
        "is_yom_tov": holiday.get("is_yom_tov"),
        "is_erev_yom_tov": holiday.get("is_erev_yom_tov"),
        "holiday": holiday.get("holiday_name"),
        "holiday_key": holiday.get("holiday_key"),
        "type": holiday.get("type"),

        # Zmanim
        **zmanim
    }


# -----------------------
# ROUTES
# -----------------------

# HEALTH
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# SIMPLE STATUS (static)
@app.route("/status")
def status():
    d = load_date()

    if not d:
        return jsonify({
            "error": "no stored date"
        }), 400

    return jsonify(build_response(d, "using_stored_date"))


# STATUS WITH DATE (auto store)
@app.route("/status/<int:year>/<int:month>/<int:day>")
def status_with_date(year, month, day):
    try:
        d = date(year, month, day)
    except ValueError:
        return jsonify({"error": "invalid date"}), 400

    save_date(d)

    return jsonify(build_response(d, "date_from_url"))


# ZMANIM (optional query or stored date)
@app.route("/zmanim")
def zmanim_route():
    d, warning = parse_date_from_request()

    if not d:
        d = load_date()
        warning = warning or "using_stored_date"

    if not d:
        return jsonify({"error": "no date available"}), 400

    city = get_city()
    config = get_config(city)

    zmanim = calculate_zmanim(config, d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),
        "warning": warning,
        **zmanim
    })


# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
