from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun


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
# MINHAGIM
# =========================================================

MINHAGIM = {
    "standard_18": {"candle": 18, "tzeis": 42},
    "standard_20": {"candle": 20, "tzeis": 42},
    "standard_30": {"candle": 30, "tzeis": 50},
    "standard_40": {"candle": 40, "tzeis": 50},
    "rabbeinu_tam": {"candle": 18, "tzeis": 72},
    "chazon_ish": {"candle": 30, "tzeis": 90},
}


START_OPTIONS = [18, 20, 30, 40]
END_OPTIONS = [42, 50, 72, 90]


# =========================================================
# CORE ENGINE
# =========================================================

def calculate_zmanim(config, date_obj):

    # -------------------------
    # LOCATION / TIMEZONE
    # -------------------------
    tz = pytz.timezone(config.get("timezone", "UTC"))

    location = LocationInfo(
        name=config.get("city", "unknown"),
        region="",
        timezone=str(tz),
        latitude=float(config.get("latitude", 0)),
        longitude=float(config.get("longitude", 0))
    )

    # -------------------------
    # SUN DATA
    # -------------------------
    s = sun(location.observer, date=date_obj, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # =====================================================
    # HALACHIC BASE
    # =====================================================

    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)

    # Plag HaMincha (Gra method)
    plag = sunset - (1.25 * shaah_zmanit)

    # Netz HaChama
    netz_hachama = sunrise

    # =====================================================
    # SOF ZMANIM (GRA + M.A.)
    # =====================================================

    sof_shema_gra = sunrise + (3 * shaah_zmanit)
    sof_shema_ma = sunrise + (2.4 * shaah_zmanit)

    sof_tefila_gra = sof_shema_gra
    sof_tefila_ma = sof_shema_ma

    # =====================================================
    # MINHAG
    # =====================================================

    minhag_key = config.get("minhag", "standard_18")
    minhag = MINHAGIM.get(minhag_key, MINHAGIM["standard_18"])

    candle_lighting = before(sunset, minhag["candle"])
    tzeis = after(sunset, minhag["tzeis"])

    # =====================================================
    # OPTIONS (LOXONE RADIO UI)
    # =====================================================

    start_options = [
        {
            "id": f"candle_{m}",
            "label": f"Candle {m} min before sunset",
            "time": fmt(before(sunset, m)),
            "ts": ts(before(sunset, m))
        }
        for m in START_OPTIONS
    ]

    end_options = [
        {
            "id": f"tzeis_{m}",
            "label": f"Tzeis {m} min after sunset",
            "time": fmt(after(sunset, m)),
            "ts": ts(after(sunset, m))
        }
        for m in END_OPTIONS
    ]

    # defaults
    default_start = min(start_options, key=lambda x: x["ts"])
    default_end = max(end_options, key=lambda x: x["ts"])

    # =====================================================
    # OUTPUT (LOXONE READY)
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
            "netz_hachama": fmt(netz_hachama),
            "sunrise_ts": ts(sunrise),
            "sunset_ts": ts(sunset)
        },

        "halacha": {
            "chatzos": fmt(chazos),
            "plag_hamincha": fmt(plag),

            "sof_zman_krias_shema": {
                "gra": {
                    "time": fmt(sof_shema_gra),
                    "ts": ts(sof_shema_gra)
                },
                "magen_avraham": {
                    "time": fmt(sof_shema_ma),
                    "ts": ts(sof_shema_ma)
                }
            },

            "sof_zman_tefila": {
                "gra": {
                    "time": fmt(sof_tefila_gra),
                    "ts": ts(sof_tefila_gra)
                },
                "magen_avraham": {
                    "time": fmt(sof_tefila_ma),
                    "ts": ts(sof_tefila_ma)
                }
            }
        },

        "shabbat": {
            "candle_lighting": {
                "time": fmt(candle_lighting),
                "ts": ts(candle_lighting)
            },
            "tzeis": {
                "time": fmt(tzeis),
                "ts": ts(tzeis)
            }
        },

        "options": {
            "start": start_options,
            "end": end_options
        },

        "defaults": {
            "start": default_start,
            "end": default_end
        }
    }
