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
        "status": "ok"
    })


# =========================================================
# MAIN API ENDPOINT
# =========================================================
@app.route("/api", methods=["GET"])
def api():

    try:
        # 1. DATE
        date = get_current_date(request)

        # 2. CONFIG
        config = load_config()

        # 3. HEBREW DATE
        hebrew = get_hebrew_date(date)

        # 4. EVENT SAFE
        event = get_event(
            hebrew["hebrew_month"],
            hebrew["hebrew_day"]
        )

        if event is None:
            event = "0"

        # 5. ZMANIM
        zmanim = calculate_zmanim(config, date)

        # 6. RESPONSE
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
# OPTIONAL
# =========================================================
def get_app():
    return app
