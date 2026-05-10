from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz


# =========================================================
# HELPERS
# =========================================================

UTC = pytz.UTC


def fmt(dt):
    return dt.strftime("%H:%M")


def ts(dt):
    return int(dt.astimezone(UTC).timestamp())


def before(dt, minutes):
    return dt - timedelta(minutes=minutes)


def after(dt, minutes):
    return dt + timedelta(minutes=minutes)


# =========================================================
# MAIN FUNCTION (IMPORTANT: MATCHS api.py)
# =========================================================

def calculate_zmanim(config, date_obj):
    """
    Main entry point used by api.py
    MUST stay stable (contract function)
    """

    tz = pytz.timezone(config.get("timezone", "UTC"))

    location = LocationInfo(
        name=config.get("city", "unknown"),
        region="",
        timezone=str(tz),
        latitude=float(config.get("latitude", 0)),
        longitude=float(config.get("longitude", 0))
    )

    # =====================================================
    # SUN DATA
    # =====================================================
    s = sun(location.observer, date=date_obj, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # =====================================================
    # CORE HALACHIC CALCULATIONS
    # =====================================================
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    netz_hachama = sunrise
    chatzos = sunrise + (day_length / 2)
    plag_hamincha = sunset - (1.25 * shaah_zmanit)

    # Sof zmanim (2 opinions)
    sof_shema_gra = sunrise + (3 * shaah_zmanit)
    sof_shema_ma = sunrise + (2.4 * shaah_zmanit)

    sof_tefila_gra = sof_shema_gra
    sof_tefila_ma = sof_shema_ma

    # =====================================================
    # SHABBAT OPTIONS (NO DECISION LOGIC)
    # =====================================================
    candle_options = [18, 20, 30, 40]
    tzeis_options = [42, 50, 72, 90]

    candle_list = [
        {
            "id": f"c{m}",
            "label": f"{m} min before sunset",
            "time": fmt(before(sunset, m)),
            "ts": ts(before(sunset, m))
        }
        for m in candle_options
    ]

    tzeis_list = [
        {
            "id": f"t{m}",
            "label": f"{m} min after sunset",
            "time": fmt(after(sunset, m)),
            "ts": ts(after(sunset, m))
        }
        for m in tzeis_options
    ]

    # =====================================================
    # OUTPUT (STABLE CONTRACT FOR api.py)
    # =====================================================
    return {
        "astronomy": {
            "sunrise": fmt(sunrise),
            "sunset": fmt(sunset),
            "netz_hachama": fmt(netz_hachama),
            "sunrise_ts": ts(sunrise),
            "sunset_ts": ts(sunset)
        },

        "halacha": {
            "chatzos": fmt(chatzos),
            "plag_hamincha": fmt(plag_hamincha),

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
