from flask import Flask, jsonify, request
from datetime import datetime
import json
import os

from app.zmanim import (
    calculate_zmanim,
    get_hebrew_date,
    get_holiday_info
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATE_FILE = os.path.join(
    BASE_DIR,
    "config",
    "current_date.json"
)

SETTINGS_FILE = os.path.join(
    BASE_DIR,
    "config",
    "settings.json"
)


# -----------------------
# LOAD CONFIG
# -----------------------
def load_config():

    if not os.path.exists(SETTINGS_FILE):

        return {
            "city": "Brussels",
            "timezone": "Europe/Brussels",
            "latitude": 50.85,
            "longitude": 4.35,
            "alos": 72,
            "tzeis": 40,
            "candle_lighting": 18
        }

    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)


# -----------------------
# SAVE DATE
# -----------------------
def save_date(d):

    with open(DATE_FILE, "w") as f:

        json.dump({
            "date": d.isoformat()
        }, f)


# -----------------------
# LOAD DATE
# -----------------------
def load_date():

    if not os.path.exists(DATE_FILE):
        return None

    try:

        with open(DATE_FILE, "r") as f:
            data = json.load(f)

        return datetime.strptime(
            data["date"],
            "%Y-%m-%d"
        ).date()

    except:
        return None


# -----------------------
# PARSE DATE
#
# Supported:
#
# /api?d=20260112
# /api?d=2026-01-12
# /api?d=2026/01/12
#
# /api?y=2026&m=1&d=12
# -----------------------
def parse_date():

    # -----------------------
    # Separate Y/M/D
    # -----------------------
    year = request.args.get("y")
    month = request.args.get("m")
    day = request.args.get("d")

    if year and month and day:

        return datetime.strptime(
            f"{year}-{month}-{day}",
            "%Y-%m-%d"
        ).date()

    # -----------------------
    # Single d parameter
    # -----------------------
    raw = request.args.get("d")

    if not raw:
        return None

    raw = raw.strip()
    raw = raw.replace("/", "-")

    # YYYY-MM-DD
    if "-" in raw:

        return datetime.strptime(
            raw,
            "%Y-%m-%d"
        ).date()

    # YYYYMMDD
    return datetime.strptime(
        raw,
        "%Y%m%d"
    ).date()


# -----------------------
# HEALTH
# -----------------------
@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


# -----------------------
# API
# -----------------------
@app.route("/api")
def api():

    try:

        d = parse_date()

        # -----------------------
        # DATE FROM REQUEST
        # -----------------------
        if d:

            save_date(d)

            warning = "date_from_request"

        # -----------------------
        # STORED DATE
        # -----------------------
        else:

            d = load_date()

            if d is None:

                return jsonify({
                    "error": "no stored date"
                }), 400

            warning = "using_stored_date"

    except:

        return jsonify({
            "error": "invalid date format"
        }), 400

    # -----------------------
    # CONFIG
    # -----------------------
    config = load_config()

    # -----------------------
    # CALCULATIONS
    # -----------------------
    zmanim = calculate_zmanim(config, d)

    hebrew = get_hebrew_date(d)

    holiday = get_holiday_info(d)

    # -----------------------
    # RESPONSE
    # -----------------------
    return jsonify({

        "status": "ok",

        "warning": warning,

        "date": d.isoformat(),

        # Hebrew
        "hebrew": hebrew,

        # Holiday
        "holiday": holiday,

        # Zmanim
        **zmanim
    })
