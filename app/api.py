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
        json.dump({"date": d.isoformat()}, f)


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
# DATE PARSER (LOXONE PRO)
# -----------------------
def parse_date():

    current = load_date()

    if current is None:
        current = datetime.today().date()

    # Loxone inputs
    y = request.args.get("y")
    m = request.args.get("m")
    d = request.args.get("d")

    # -----------------------
    # PARTIAL UPDATE MODE
    # -----------------------
    if y or m or d:

        year = int(y) if y else current.year
        month = int(m) if m else current.month
        day = int(d) if d else current.day

        return datetime.strptime(
            f"{year}-{month}-{day}",
            "%Y-%m-%d"
        ).date()

    # -----------------------
    # FULL DATE MODE
    # -----------------------
    raw = request.args.get("date") or request.args.get("d")

    if not raw:
        return None

    raw = raw.strip().replace("/", "-")

    try:

        if "-" in raw:
            return datetime.strptime(raw, "%Y-%m-%d").date()

        return datetime.strptime(raw, "%Y%m%d").date()

    except:
        return None


# -----------------------
# HEALTH
# -----------------------
@app.route("/health")
def health():

    return jsonify({"status": "ok"})


# -----------------------
# API
# -----------------------
@app.route("/api")
def api():

    d = parse_date()

    # -----------------------
    # NO DATE
    # -----------------------
    if d is None:
        return jsonify({
            "error": "no valid date provided"
        }), 400

    save_date(d)

    config = load_config()

    zmanim = calculate_zmanim(config, d)
    hebrew = get_hebrew_date(d)
    holiday = get_holiday_info(d)

    return jsonify({

        "status": "ok",

        "date": d.isoformat(),

        "hebrew": hebrew,
        "holiday": holiday,

        **zmanim
    })
