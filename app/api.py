from flask import Flask, jsonify, request
from datetime import datetime
from app.zmanim import calculate_zmanim, get_hebrew_date, get_holiday_info

app = Flask(__name__)

# -----------------------
# HEALTH CHECK
# -----------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# -----------------------
# API ENDPOINT
# -----------------------
@app.route("/api")
def api():

    raw = request.args.get("d")

    if not raw:
        return jsonify({"error": "missing date (d=YYYYMMDD)"}), 400

    try:
        raw = raw.replace("-", "")
        d = datetime.strptime(raw, "%Y%m%d").date()
    except:
        return jsonify({"error": "invalid date format"}), 400

    # 🔧 simpele default config (kan later uit JSON)
    config = {
        "city": "Brussels",
        "timezone": "Europe/Brussels",
        "latitude": 50.85,
        "longitude": 4.35,
        "alos": 72,
        "tzeis": 40,
        "candle_lighting": 18
    }

    zmanim = calculate_zmanim(config, d)
    hebrew = get_hebrew_date(d)
    holiday = get_holiday_info(d)

    return jsonify({
        "date": d.isoformat(),
        "hebrew": hebrew,
        "holiday": holiday,
        "zmanim": zmanim
    })
