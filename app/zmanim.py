from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
from pyluach import dates


# =========================================================
# HELPERS
# =========================================================

def format_time(dt):
    return dt.strftime("%H:%M")


def to_timestamp(dt):
    return int(dt.timestamp())


# =========================================================
# SAFE CONFIG READER
# =========================================================

def get_value(config, key, default):
    value = config.get(key, default)

    if isinstance(value, dict):
        return value.get("minutes", default)

    if isinstance(value, (int, float)):
        return value

    return default


# =========================================================
# MINHAGIM (SHABBES LOGICA)
# =========================================================

START_OPTIONS = [18, 20, 30, 40]
END_OPTIONS = [42, 50, 72, 90]

MINHAGIM = {
    "standard_18": {"candle": 18, "tzeis": 42},
    "standard_20": {"candle": 20, "tzeis": 42},
    "standard_30": {"candle": 30, "tzeis": 50},
    "standard_40": {"candle": 40, "tzeis": 50},

    "rabbeinu_tam": {"candle": 18, "tzeis": 72},
    "chazon_ish": {"candle": 30, "tzeis": 90},
    "yerushalayim": {"candle": 40, "tzeis": 50}
}


# =========================================================
# CORE ENGINE
# =========================================================

def calculate_zmanim(config, d):

    city = config.get("city", "unknown")
    tz = config.get("timezone", "UTC")

    location = LocationInfo(
        name=city,
        region="",
        timezone=tz,
        latitude=float(config.get("latitude", 0)),
        longitude=float(config.get("longitude", 0))
    )

    s = sun(location.observer, date=d, tzinfo=pytz.timezone(tz))

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # ----------------------------
    # HALACHIC BASE CALCULATION
    # ----------------------------
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)
    plag = sunset - (1.25 * shaah_zmanit)

    # ----------------------------
    # MINHAG SELECTION
    # ----------------------------
    minhag_key = config.get("minhag", "standard_18")
    minhag = MINHAGIM.get(minhag_key, MINHAGIM["standard_18"])

    candle_offset = minhag["candle"]
    tzeis_offset = minhag["tzeis"]

    # ----------------------------
    # BASE TIMES
    # ----------------------------
    alos_min = get_value(config, "alos", 72)

    alos = sunrise - timedelta(minutes=alos_min)
    tzeis = sunset + timedelta(minutes=tzeis_offset)
    candle = sunset - timedelta(minutes=candle_offset)

    # ----------------------------
    # SHABBES OPTIONS (START + END)
    # ----------------------------

    start_times = {}
    end_times = {}

    for m in START_OPTIONS:
        t = sunset - timedelta(minutes=m)
        start_times[str(m)] = {
            "time": format_time(t),
            "ts": to_timestamp(t)
        }

    for m in END_OPTIONS:
        t = sunset + timedelta(minutes=m)
        end_times[str(m)] = {
            "time": format_time(t),
            "ts": to_timestamp(t)
        }

    # earliest / latest helpers
    start_times["earliest"] = min(start_times.values(), key=lambda x: x["ts"])
    end_times["latest"] = max(end_times.values(), key=lambda x: x["ts"])

    # ----------------------------
    # OUTPUT
    # ----------------------------
    return {
        "city": city,
        "date": d.isoformat(),

        # CORE TIMES
        "sunrise": format_time(sunrise),
        "sunset": format_time(sunset),
        "shkia": format_time(sunset),

        "alos": format_time(alos),
        "tzeis": format_time(tzeis),
        "candle_lighting": format_time(candle),

        "chatzos": format_time(chatzos),
        "plag": format_time(plag),

        # TIMESTAMPS
        "sunrise_ts": to_timestamp(sunrise),
        "sunset_ts": to_timestamp(sunset),
        "plag_ts": to_timestamp(plag),
        "tzeis_ts": to_timestamp(tzeis),

        # MINHAG INFO
        "minhag": minhag_key,

        # SHABBES OPTIONS (Loxone core feature)
        "shabbes": {
            "start": start_times,
            "end": end_times
        }
    }


# =========================================================
# HEBREW DATE
# =========================================================

def get_hebrew_date(d):
    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    return {
        "hebrew_date": str(h),
        "hebrew_day": h.day,
        "hebrew_month": h.month,
        "hebrew_year": h.year
    }
