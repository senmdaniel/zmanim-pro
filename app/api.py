from flask import request, jsonify
from datetime import datetime

from app.zmanim import calculate_zmanim, get_holiday_info, get_hebrew_date

@app.route("/api")
def api():

    raw = request.args.get("d")

    if not raw:
        return jsonify({"error": "missing d parameter (YYYYMMDD)"}), 400

    try:
        d = datetime.strptime(raw.replace("-", ""), "%Y%m%d").date()
    except:
        return jsonify({"error": "invalid date"}), 400

    # tijdelijke config (pas aan naar jouw settings als nodig)
    config = {
        "city": "default",
        "timezone": "Europe/Brussels",
        "latitude": 50.85,
        "longitude": 4.35
    }

    zmanim = calculate_zmanim(config, d)
    holiday = get_holiday_info(d)
    hebrew = get_hebrew_date(d)

    return jsonify({
        "date": d.isoformat(),
        "hebrew": hebrew,
        "holiday": holiday,
        "zmanim": zmanim
    })
