from flask import Flask, jsonify, request
import json
import os

from app.date_provider import get_current_date
from app.zmanim import calculate_zmanim, get_hebrew_date
from app.yomim_tovim import get_event


app = Flask(__name__)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETTINGS_FILE = os.path.join(
    BASE_DIR,
    "config",
    "settings.json"
)


# =========================================================
# CONFIG
# =========================================================

def load_config():

    if not os.path.exists(SETTINGS_FILE):

        return {
            "city": "Brussels",
            "timezone": "Europe/Brussels",
            "latitude": 50.85,
            "longitude": 4.35,

            # default minhag
            "minhag": "standard_18",

            # optional defaults
            "alos": 72
        }

    try:

        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)

    except:

        # safe fallback
        return {
            "city": "Brussels",
            "timezone": "Europe/Brussels",
            "latitude": 50.85,
            "longitude": 4.35,
            "minhag": "standard_18",
            "alos": 72
        }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok"
    })


# =========================================================
# MAIN API
# =========================================================

@app.route("/api", methods=["GET", "POST"])
def api():

    try:

        # -------------------------------------------------
        # DATE PROVIDER
        # single source of truth
        # -------------------------------------------------

        d = get_current_date(request)

        # -------------------------------------------------
        # CONFIG
        # -------------------------------------------------

        config = load_config()

        # -------------------------------------------------
        # ZMANIM
        # -------------------------------------------------

        zmanim = calculate_zmanim(config, d)

        # -------------------------------------------------
        # HEBREW DATE
        # -------------------------------------------------

        hebrew = get_hebrew_date(d)

        # -------------------------------------------------
        # EVENTS / YOMIM TOVIM
        # -------------------------------------------------

        event = get_event(
            hebrew["hebrew_month"],
            hebrew["hebrew_day"]
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "status": "ok",

            # gregorian
            "date": d.isoformat(),

            # jewish calendar
            "hebrew": hebrew,

            # yom tov / erev yom tov
            "event": event,

            # all zmanim
            "zmanim": zmanim

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "error": str(e)

        }), 500
