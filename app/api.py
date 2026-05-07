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
# HEALTH
# -----------------------
@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


# -----------------------
# API
# /api?d=20260101
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
            raw = raw.replace("-", "")
            d = datetime.strptime(
                raw,
                "%Y%m%d"
            ).date()

            save_date(d)

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

    # -----------------------
    # CONFIG
    # -----------------------
    config = {
        "city": "Brussels",
        "timezone": "Europe/Brussels",
        "latitude": 50.85,
        "longitude": 4.35,
        "alos": 72,
        "tzeis": 40,
        "candle_lighting": 18
    }

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
        "date": d.isoformat(),
        "hebrew": hebrew,
        "holiday": holiday,
        **zmanim
    })
