from flask import Flask, jsonify, request
from datetime import date, datetime
import json
import os


app = Flask(__name__)

@app.route("/status")
def status():
    return jsonify({
        "status": "online",
        "service": "zmanim-pro"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORED_DATE_PATH = os.path.join(BASE_DIR, "config", "current_date.json")

from app.zmanim import (
    calculate_zmanim,
    get_holiday_info,
    get_hebrew_date
)

app = Flask(__name__)



# -----------------------
# CONFIG LOADER
# -----------------------
def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


def get_config(city):
    """
    Bouw config object dat zmanim.py verwacht
    """
    path = os.path.join(BASE_DIR, "config", "settings.json")

    with open(path, "r") as f:
        cfg = json.load(f)

    cfg["city"] = city
    return cfg

# -----------------------
# HELPERS
# -----------------------

def save_date(d):
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

# -----------------------
# DATE PARSER
# -----------------------
def parse_date():
    raw = request.args.get("date") or request.args.get("datum")

    # 👉 ALS Loxone iets stuurt → opslaan
    if raw:
        raw_clean = raw.replace("/", "-")

        try:
            d = datetime.strptime(raw_clean, "%Y-%m-%d").date()
            save_date(d)
            return d, "date_updated_from_request"
        except ValueError:
            return None, f"invalid_date_format:{raw}"

    # 👉 ANDERS → opgeslagen datum gebruiken
    stored = load_date()

    if stored:
        return stored, "using_stored_date"

    return None, "no_date_available"
# -----------------------
# STATUS ENDPOINT
# -----------------------
@app.route("/status/<datum>")
def status(datum):

    try:
        d = datetime.strptime(datum, "%Y-%m-%d").date()
    except:
        return jsonify({"error": "invalid date"}), 400

    city = get_city()
    warning = "date_from_url"

    if d is None:
        return jsonify({"error": warning}), 400

    config = get_config(city)

    zmanim = calculate_zmanim(config, d)
    holiday = get_holiday_info(d)
    hebrew = get_hebrew_date(d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),

        # Hebrew
        "hebrew_date": hebrew["hebrew_date"],
        "hebrew_day": hebrew["hebrew_day"],
        "hebrew_month": hebrew["hebrew_month"],
        "hebrew_year": hebrew["hebrew_year"],

        # Debug
        "warning": warning,

        # Holiday state
        "is_yom_tov": holiday.get("is_yom_tov"),
        "is_erev_yom_tov": holiday.get("is_erev_yom_tov"),
        "holiday": holiday.get("holiday_name"),
        "holiday_key": holiday.get("holiday_key"),
        "type": holiday.get("type"),

        # Zmanim
        **zmanim
    })

# -----------------------
# STATUS WITH URL DATE
# Example:
# /status/2026/07/01
# -----------------------
@app.route("/status/<year>/<month>/<day>")
def status_with_date(year, month, day):

    city = get_city()

    try:
        d = datetime.strptime(
            f"{year}-{month}-{day}",
            "%Y-%m-%d"
        ).date()

        save_date(d)

    except ValueError:
        return jsonify({"error": "invalid_date"}), 400

    config = get_config(city)

    zmanim = calculate_zmanim(config, d)
    holiday = get_holiday_info(d)
    hebrew = get_hebrew_date(d)

    return jsonify({
        "city": city,
        "date": d.isoformat(),

        "hebrew_date": hebrew["hebrew_date"],
        "hebrew_day": hebrew["hebrew_day"],
        "hebrew_month": hebrew["hebrew_month"],
        "hebrew_year": hebrew["hebrew_year"],

        "warning": "date_from_url",

        "is_yom_tov": holiday.get("is_yom_tov"),
        "is_erev_yom_tov": holiday.get("is_erev_yom_tov"),
        "holiday": holiday.get("holiday_name"),
        "holiday_key": holiday.get("holiday_key"),
        "type": holiday.get("type"),

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

    config = get_config(city)

    zmanim = calculate_zmanim(config, d)

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
