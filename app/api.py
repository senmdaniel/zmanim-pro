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
# CONFIG
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
# DATE SAVE
# -----------------------
def save_date(d):

    with open(DATE_FILE, "w") as f:
        json.dump({"date": d.isoformat()}, f)


# -----------------------
# DATE LOAD
# -----------------------
def load_date():

    if not os.path.exists(DATE_FILE):
        return None

    try:
        with open(DATE_FILE, "r") as f:
            data = json.load(f)

        return datetime.strptime(data["date"], "%Y-%m-%d").date()

    except:
        return None


# -----------------------
# CLEAN Loxone INPUT
# -----------------------
def clean(v):

    if v in [None, "", "None", "null"]:
        return None

    return v


# -----------------------
# PARSE DATE (LOXONE SAFE)
# -----------------------
def parse_date():

    current = load_date() or datetime.today().date()

    # Loxone inputs (GET or POST safe)
    y = clean(request.values.get("y"))
    m = clean(request.values.get("m"))
    d = clean(request.values.get("d"))
    raw = clean(request.values.get("date"))

    # -----------------------
    # FULL DATE MODE
    # -----------------------
    if raw:

        raw = raw.replace("/", "-")

        try:
            if "-" in raw:
                return datetime.strptime(raw, "%Y-%m-%d").date()

            return datetime.strptime(raw, "%Y%m%d").date()

        except:
            return None

    # -----------------------
    # PARTIAL MODE (LOXONE BEST)
    # -----------------------
    try:

        year = int(y) if y else current.year
        month = int(m) if m else current.month
        day = int(d) if d else current.day

        return datetime(year, month, day).date()

    except:
        return None


# -----------------------
# HEALTH CHECK
# -----------------------
@app.route("/health", methods=["GET"])
def health():

    return jsonify({"status": "ok"})


# -----------------------
# MAIN API
# -----------------------
@app.route("/api", methods=["GET", "POST"])
def api():

    d = parse_date()

    if d is None:
        return jsonify({
            "status": "error",
            "error": "invalid or missing date"
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
