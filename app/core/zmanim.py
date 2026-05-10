from datetime import datetime, timedelta
import pytz
from flask import Flask, request, jsonify
from astral import LocationInfo
from astral.sun import sun


app = Flask(__name__)

UTC = pytz.UTC


# =========================================================
# HELPERS
# =========================================================

def fmt(dt):
    return dt.strftime("%H:%M")


def ts(dt):
    return int(dt.astimezone(UTC).timestamp())


def before(dt, minutes):
    return dt - timedelta(minutes=minutes)


def after(dt, minutes):
    return dt + timedelta(minutes=minutes)


# =========================================================
# CORE CALCULATION ENGINE
# =========================================================

def calculate_all_times(date_obj, config):

    tz = pytz.timezone(config.get("timezone", "UTC"))

    location = LocationInfo(
        name=config.get("city", "unknown"),
        region="",
        timezone=str(tz),
        latitude=float(config.get("latitude", 0)),
        longitude=float(config.get("longitude", 0))
    )

    s = sun(location.observer, date=date_obj, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # =====================================================
    # HALACHIC CORE
    # =====================================================

    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    netz = sunrise
    chatzos = sunrise + (day_length / 2)
    plag = sunset - (1.25 * shaah_zmanit)

    sof_shema_gra = sunrise + (3 * shaah_zmanit)
    sof_shema_ma = sunrise + (2.4 * shaah_zmanit)

    sof_tefila_gra = sof_shema_gra
    sof_tefila_ma = sof_shema_ma

    # =====================================================
    # SHABBAT OPTIONS (NO DECISION MAKING)
    # =====================================================

    candle_options = [18, 20, 30, 40]
    tzeis_options = [42, 50, 72, 90]

    candle_list = []
    tzeis_list = []

    for m in candle_options:
        t = before(sunset, m)
        candle_list.append({
            "id": f"c{m}",
            "label": f"{m} min before sunset",
            "time": fmt(t),
            "ts": ts(t)
        })

    for m in tzeis_options:
        t = after(sunset, m)
        tzeis_list.append({
            "id": f"t{m}",
            "label": f"{m} min after sunset",
            "time": fmt(t),
            "ts": ts(t)
        })

    # =====================================================
    # RESPONSE (FULL DATA ONLY)
    # =====================================================

    return {
        "meta": {
            "city": config.get("city"),
            "date": date_obj.isoformat(),
            "timezone": config.get("timezone")
        },

        "astronomy": {
            "sunrise": fmt(sunrise),
            "sunset": fmt(sunset),
            "netz_hachama": fmt(netz),
            "sunrise_ts": ts(sunrise),
            "sunset_ts": ts(sunset)
        },

        "halacha": {
            "chatzos": fmt(chatzos),
            "plag_hamincha": fmt(plag),

            "sof_zman_krias_shema": {
                "gra": fmt(sof_shema_gra),
                "magen_avraham": fmt(sof_shema_ma)
            },

            "sof_zman_tefila": {
                "gra": fmt(sof_tefila_gra),
                "magen_avraham": fmt(sof_tefila_ma)
            }
        },

        "shabbat_options": {
            "candle_lighting": candle_list,
            "tzeis": tzeis_list
        }
    }


# =========================================================
# API ENDPOINT
# =========================================================

@app.route("/zmanim", methods=["GET"])
def zmanim():

    y = int(request.args.get("y"))
    m = int(request.args.get("m"))
    d = int(request.args.get("d"))

    date_obj = datetime(y, m, d)

    config = {
        "city": request.args.get("city", "Brussels"),
        "timezone": request.args.get("tz", "Europe/Brussels"),
        "latitude": request.args.get("lat", 50.85),
        "longitude": request.args.get("lon", 4.35)
    }

    return jsonify(calculate_all_times(date_obj, config))


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
