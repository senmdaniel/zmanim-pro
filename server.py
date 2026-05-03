from flask import Flask, request, jsonify
from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
from convertdate import hebrew
from yom_tov import get_yom_tov_day, is_yom_tov
import datetime
import json
import os

from yom_tov import get_yom_tov_day, is_yom_tov

app = Flask(__name__)

# ---------------------------
# CONFIG
# ---------------------------

CONFIG_PATH = "/opt/zmanim/config.json"

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
# HELPERS
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
# API
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

        # Zmanim
        alos = zc.alos()
        netz = zc.sunrise()
        shkia = zc.sunset()
        tzeit = zc.tzais()

        chatzot = zc.chatzos()
        mincha_gedola = zc.mincha_gedola()
        plag = zc.plag_hamincha()

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

        # YOM TOV LOGIC
        yom_tov_day = get_yom_tov_day(date)
        is_yom_tov_flag = yom_tov_day is not None

        erev_yom_tov_flag = get_yom_tov_day(date + datetime.timedelta(days=1)) is not None

        return jsonify({
            "date": date.strftime("%Y-%m-%d"),
            "city": city,

            "hebrew": hebrew_date,

            # zmanim
            "alos": fmt(alos),
            "netz": fmt(netz),
            "chatzot": fmt(chatzot),
            "mincha_gedola": fmt(mincha_gedola),
            "plag": fmt(plag),
            "shkia": fmt(shkia),
            "tzeit": fmt(tzeit),

            "sof_zman_shma_gra": fmt(sof_shma_gra),
            "sof_zman_tfila_gra": fmt(sof_tfila_gra),
            "sof_zman_shma_ma": fmt(sof_shma_ma),
            "sof_zman_tfila_ma": fmt(sof_tfila_ma),

            # 🔥 YOM TOV (LOXONE READY)
            "is_yom_tov": is_yom_tov_flag,
            "yom_tov_day": yom_tov_day,
            "is_erev_yom_tov": erev_yom_tov_flag
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
