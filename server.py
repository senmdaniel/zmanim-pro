from flask import Flask, request, jsonify
from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
from convertdate import hebrew
import datetime
import json
import os

app = Flask(__name__)

# ---------------------------
# CONFIG
# ---------------------------

CONFIG_PATH = "/home/mjd/zmanim-pro/config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"city": "antwerp"}

CITIES = {
    "antwerp": (51.2194, 4.4025, "Europe/Brussels"),
    "jerusalem": (31.7683, 35.2137, "Asia/Jerusalem"),
    "london": (51.5074, -0.1278, "Europe/London")
}

# ---------------------------
# Helpers
# ---------------------------

def fmt(t):
    try:
        return t.strftime("%H:%M") if t else None
    except:
        return None

def parse_date(date_str):
    try:
        if not date_str:
            return datetime.date.today()
        y, m, d = map(int, date_str.split("-"))
        return datetime.date(y, m, d)
    except:
        return None

# ---------------------------
# Endpoint
# ---------------------------

@app.route("/zmanim", methods=["GET"])
def zmanim():

    try:
        config = load_config()

        date_str = request.args.get("date")
        date = parse_date(date_str)

        if not date:
            return jsonify({"error": "Invalid date"}), 400

        city = config.get("city", "antwerp")

        lat, lon, tz = CITIES.get(city, CITIES["antwerp"])

        location = GeoLocation(city, lat, lon, tz)

        zc = ZmanimCalendar(geo_location=location)
        zc.date = date

        # tijden
        alos = zc.alos()
        netz = zc.sunrise()
        shkia = zc.sunset()
        tzeit = zc.tzais()

        chatzot = zc.chatzos()
        mincha_gedola = zc.mincha_gedola()
        plag = zc.plag_hamincha()

        # 🔥 eigen MA plag
        try:
            if alos and tzeit:
                day_length = (tzeit - alos)
                plag_ma = alos + day_length * (10.75 / 12)
            else:
                plag_ma = None
        except:
            plag_ma = None

        sof_shma_gra = zc.sof_zman_shma_gra()
        sof_tfila_gra = zc.sof_zman_tfila_gra()
        sof_shma_ma = zc.sof_zman_shma_mga()
        sof_tfila_ma = zc.sof_zman_tfila_mga()

        # Hebreeuwse datum
        try:
            h = hebrew.from_gregorian(date.year, date.month, date.day)
            hebrew_date = f"{int(h[2]):02}-{int(h[1]):02}-{int(h[0])}"
        except:
            hebrew_date = None

        return jsonify({
            "date": date.strftime("%Y-%m-%d"),

            "alos": fmt(alos),
            "netz": fmt(netz),

            "chatzot": fmt(chatzot),
            "mincha_gedola": fmt(mincha_gedola),

            "plag": fmt(plag),
            "plag_ma": fmt(plag_ma),

            "shkia": fmt(shkia),
            "tzeit": fmt(tzeit),

            "sof_zman_shma_gra": fmt(sof_shma_gra),
            "sof_zman_tfila_gra": fmt(sof_tfila_gra),
            "sof_zman_shma_ma": fmt(sof_shma_ma),
            "sof_zman_tfila_ma": fmt(sof_tfila_ma),

            "hebrew": hebrew_date,
            "city": city
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
