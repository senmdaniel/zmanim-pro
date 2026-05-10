from flask import Flask, jsonify, request

from app.core.date_provider import get_current_date
from app.core.zmanim import calculate_zmanim
from app.core.hebrew_calendar import get_hebrew_date
from app.data.events import get_event
from app.core.config import load_config

app = Flask(__name__)


# =========================================================
# HEALTH CHECK
# =========================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok!!!!!!!!!"
    })


# =========================================================
# MAIN API ENDPOINT
# =========================================================
@app.route("/api", methods=["GET"])
def api():

    try:
        # -------------------------------------------------
        # 1. DATE (from request or system fallback)
        # -------------------------------------------------
        date = get_current_date(request)

        # -------------------------------------------------
        # 2. CONFIG (city, location, etc.)
        # -------------------------------------------------
        config = load_config()

        # -------------------------------------------------
        # 3. HEBREW DATE (OFFLINE, CORRECT)
        # -------------------------------------------------
        hebrew = get_hebrew_date(date)

        # -------------------------------------------------
        # 4. EVENTS (YOMIM TOVIM)
        # -------------------------------------------------
        "event": event if event else 0,
            hebrew["hebrew_month"],
            hebrew["hebrew_day"]
        )

        # -------------------------------------------------
        # 5. ZMANIM CALCULATION
        # -------------------------------------------------
        zmanim = calculate_zmanim(config, date)

        # -------------------------------------------------
        # 6. RESPONSE
        # -------------------------------------------------
        return jsonify({
            "status": "ok",

            "date": date.isoformat(),

            "hebrew": hebrew,

            "event": event,

            "zmanim": zmanim,

            "location": {
                "city": config.get("city"),
                "timezone": config.get("timezone"),
                "latitude": config.get("latitude"),
                "longitude": config.get("longitude")
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# =========================================================
# OPTIONAL: expose app for run.py
# =========================================================
def get_app():
    return app
