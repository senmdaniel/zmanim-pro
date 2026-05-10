from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
from pyluach import dates


# =========================================================
# HELPERS
# =========================================================

UTC = pytz.UTC


def format_time(dt):
    return dt.strftime("%H:%M")


def to_timestamp(dt):
    return int(
        dt.astimezone(UTC).timestamp()
    )


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
# SHABBES OPTIONS
# =========================================================

START_OPTIONS = [18, 20, 30, 40]
END_OPTIONS = [42, 50, 72, 90]


# =========================================================
# MINHAGIM
# =========================================================

MINHAGIM = {

    "standard_18": {
        "name": "Standard 18",
        "candle": 18,
        "tzeis": 42
    },

    "standard_20": {
        "name": "Standard 20",
        "candle": 20,
        "tzeis": 42
    },

    "standard_30": {
        "name": "Standard 30",
        "candle": 30,
        "tzeis": 50
    },

    "standard_40": {
        "name": "Standard 40",
        "candle": 40,
        "tzeis": 50
    },

    "rabbeinu_tam": {
        "name": "Rabbeinu Tam",
        "candle": 18,
        "tzeis": 72
    },

    "chazon_ish": {
        "name": "Chazon Ish",
        "candle": 30,
        "tzeis": 90
    },

    "yerushalayim": {
        "name": "Yerushalayim",
        "candle": 40,
        "tzeis": 50
    }
}


# =========================================================
# CORE ENGINE
# =========================================================

def calculate_zmanim(config, d):

    city = config.get("city", "unknown")
    tz = config.get("timezone", "UTC")

    timezone = pytz.timezone(tz)

    location = LocationInfo(
        name=city,
        region="",
        timezone=tz,
        latitude=float(config.get("latitude", 0)),
        longitude=float(config.get("longitude", 0))
    )

    s = sun(
        location.observer,
        date=d,
        tzinfo=timezone
    )

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # =====================================================
    # HALACHIC BASE
    # =====================================================

    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)

    plag = sunset - (
        1.25 * shaah_zmanit
    )

    # =====================================================
    # MINHAG
    # =====================================================

    minhag_key = config.get(
        "minhag",
        "standard_18"
    )

    minhag = MINHAGIM.get(
        minhag_key,
        MINHAGIM["standard_18"]
    )

    candle_offset = minhag["candle"]
    tzeis_offset = minhag["tzeis"]

    # =====================================================
    # CORE TIMES
    # =====================================================

    alos_min = get_value(
        config,
        "alos",
        72
    )

    alos = sunrise - timedelta(
        minutes=alos_min
    )

    candle = sunset - timedelta(
        minutes=candle_offset
    )

    tzeis = sunset + timedelta(
        minutes=tzeis_offset
    )

    # =====================================================
    # SHABBES OPTIONS
    # =====================================================

    start_times = {}
    end_times = {}

    start_values = []
    end_values = []

    for m in START_OPTIONS:

        t = sunset - timedelta(minutes=m)

        obj = {
            "time": format_time(t),
            "ts": to_timestamp(t)
        }

        start_times[str(m)] = obj
        start_values.append(obj)

    for m in END_OPTIONS:

        t = sunset + timedelta(minutes=m)

        obj = {
            "time": format_time(t),
            "ts": to_timestamp(t)
        }

        end_times[str(m)] = obj
        end_values.append(obj)

    # safe helpers
    start_times["earliest"] = min(
        start_values,
        key=lambda x: x["ts"]
    )

    end_times["latest"] = max(
        end_values,
        key=lambda x: x["ts"]
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    return {

        "city": city,
        "date": d.isoformat(),

        # core
        "sunrise": format_time(sunrise),
        "shkia": format_time(sunset),

        "alos": format_time(alos),
        "tzeis": format_time(tzeis),

        "candle_lighting": format_time(candle),

        "chatzos": format_time(chatzos),
        "plag": format_time(plag),

        # timestamps
        "sunrise_ts": to_timestamp(sunrise),
        "shkia_ts": to_timestamp(sunset),

        "plag_ts": to_timestamp(plag),
        "tzeis_ts": to_timestamp(tzeis),

        # minhag
        "minhag": minhag_key,

        # shabbes
        "shabbes": {
            "start": start_times,
            "end": end_times
        }
    }


# =========================================================
# HEBREW DATE
# =========================================================

def get_hebrew_date(d):

    g = dates.GregorianDate(
        d.year,
        d.month,
        d.day
    )

    h = g.to_heb()

    return {

        "hebrew_date": str(h),

        "hebrew_day": h.day,
        "hebrew_month": h.month,
        "hebrew_year": h.year
    }
