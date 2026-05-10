from flask import Flask, jsonify, request

from app.core.date_provider import get_current_date
from app.core.zmanim import calculate_zmanim, get_hebrew_date
from app.core.calendar import get_event
from app.core.config import load_config   # we maken dit klein helper filetje

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api", methods=["GET"])
def api():

    try:
        d = get_current_date(request)
        config = load_config()

        hebrew = get_hebrew_date(d)
        zmanim = calculate_zmanim(config, d)
        event = get_event(hebrew["hebrew_month"], hebrew["hebrew_day"])

        return jsonify({
            "status": "ok",
            "date": d.isoformat(),
            "hebrew": hebrew,
            "event": event,
            "zmanim": zmanim
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
