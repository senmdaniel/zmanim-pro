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
DATE_FILE = os.path.join(BASE_DIR, "config", "current_date.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "config", "settings.json")


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
# Supports:
# 20260112
# 2026-01-12
# 2026/01/12
# -----------------------
def parse_date(raw):

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
#
# SET DATE:
# /api?d=20260112
# /api?d=2026-01-12
# /api?d=2026/01/12
#
# GET STORED DATE:
# /api
# -----------------------
@app.route("/api")
def api():

    raw = request.args.get("d")

    # -----------------------
    # DATE FROM URL
    # -----------------------
    if raw:

        try:

            d = parse_date(raw)

            # save for later /api calls
            save_date(d)

            warning = "date_from_request"

        except:
            return jsonify({
                "error": "invalid date format"
            }), 400

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
