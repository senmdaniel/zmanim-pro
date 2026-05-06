from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
import json
import os
from pyluach import dates


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------
# HELPERS
# ----------------------------
def load_overrides(city):
    try:
        path = os.path.join(BASE_DIR, "data", f"{city}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception as e:
        print("Override load error:", e)

    return {}


def apply_overrides(zmanim, overrides, date):
    try:
        key = date.isoformat()

        if key not in overrides:
            return zmanim

        allowed_keys = {
            "alos",
            "chatzos",
            "plag_hamincha",
            "shkia",
            "tzeis",
            "candle_lighting"
        }

        for k, v in overrides[key].items():
            if k in allowed_keys:
                zmanim[k] = v

        return zmanim

    except Exception as e:
        print("Override apply error:", e)
        return zmanim


def format_time(dt):
    return dt.strftime("%H:%M")


def to_timestamp(dt):
    return int(dt.timestamp())


# ----------------------------
# CORE ZMANIM ENGINE
# ----------------------------
from datetime import timedelta

def calculate_zmanim(config, d):
    """
    Clean production zmanim engine (Pi + Loxone ready)
    """

    # ----------------------------
    # VALIDATION
    # ----------------------------
    required = ["city", "latitude", "longitude", "timezone"]

    for r in required:
        if r not in config:
            raise ValueError(f"Missing config key: {r}")

    tz = pytz.timezone(config["timezone"])

    location = LocationInfo(
        name=config["city"],
        region="",
        timezone=config["timezone"],
        latitude=float(config["latitude"]),
        longitude=float(config["longitude"])
    )

    s = sun(location.observer, date=d, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # ----------------------------
    # BASE HALACHIC VALUES
    # ----------------------------
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12
    chatzos = sunrise + (day_length / 2)

    # =========================================================
    # 🌅 DAWN (ALOT HASHACHAR)
    # =========================================================
    dawn = {
        "alos_90": sunrise - timedelta(minutes=90),
        "alos_72": sunrise - timedelta(minutes=72),
        "alos_16_1": sunrise - timedelta(minutes=72)  # benadering
    }

    # =========================================================
    # 🌄 SUN
    # =========================================================
    sun_block = {
        "sunrise": sunrise,
        "sunset": sunset,
        "chatzos": chatzos
    }

    # =========================================================
    # 📖 SHEMA TIMES
    # =========================================================
    shema = {
        "gra_end_shema": sunrise + 3 * shaah_zmanit,
        "gra_end_shacharis": sunrise + 4 * shaah_zmanit
    }

    # =========================================================
    # 🕍 MINCHA
    # =========================================================
    mincha = {
        "mincha_gedola": chatzos + timedelta(minutes=30),
        "mincha_ketana": chatzos + 6 * shaah_zmanit,
        "plag_hamincha": sunset - 1.25 * shaah_zmanit
    }

    # =========================================================
    # 🌇 NIGHTFALL (TZEIS)
    # =========================================================
    tzeis = {
        "13_5": sunset + timedelta(minutes=13.5),
        "16_1": sunset + timedelta(minutes=72),
        "18": sunset + timedelta(minutes=18),
        "24": sunset + timedelta(minutes=24),
        "27": sunset + timedelta(minutes=27),
        "36": sunset + timedelta(minutes=36),
        "40": sunset + timedelta(minutes=40),
        "rt_72": sunset + timedelta(minutes=72)
    }

    # =========================================================
    # 🌌 NIGHT
    # =========================================================
    night = {
        "chatzos_laila": sunset + (day_length / 2)
    }

    # =========================================================
    # OUTPUT FLAT + LOXONE FRIENDLY
    # =========================================================
    def ts(dt):
        return int(dt.timestamp())

    def fmt(dt):
        return dt.strftime("%H:%M")

    result = {
        "city": config["city"],
        "date": d.isoformat(),

        # RAW STRUCTURE (for apps later)
        "dawn": {k: fmt(v) for k, v in dawn.items()},
        "sun": {k: fmt(v) for k, v in sun_block.items()},
        "shema": {k: fmt(v) for k, v in shema.items()},
        "mincha": {k: fmt(v) for k, v in mincha.items()},
        "tzeis": {k: fmt(v) for k, v in tzeis.items()},
        "night": {k: fmt(v) for k, v in night.items()},

        # FLAT (Loxone uses this)
        "alos": fmt(dawn["alos_72"]),
        "sunrise": fmt(sunrise),
        "sunset": fmt(sunset),
        "chatzos": fmt(chatzos),
        "plag": fmt(mincha["plag_hamincha"]),

        # timestamps
        "sunrise_ts": ts(sunrise),
        "sunset_ts": ts(sunset),
        "plag_ts": ts(mincha["plag_hamincha"]),
        "tzeis_ts": ts(tzeis["16_1"])
    }

    # ----------------------------
    # OVERRIDES (safe)
    # ----------------------------
    overrides = load_overrides(config["city"])
    result = apply_overrides(result, overrides, d)

    return result


# ----------------------------
# HEBREW DATE
# ----------------------------
def get_hebrew_date(d):
    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    return {
        "hebrew_date": str(h),
        "hebrew_day": h.day,
        "hebrew_month": h.month,
        "hebrew_year": h.year
    }


# ----------------------------
# HOLIDAY ENGINE (YOM TOV + EREV)
# ----------------------------
def get_holiday_info(d):

    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    yom_tov_days = {
        (1, 15): ("pesach 1", "Pesach", 1),
        (1, 16): ("pesach 2", "Pesach", 2),
        (1, 21): ("pesach 7", "Pesach", 7),
        (1, 22): ("pesach 8", "Pesach", 8),

        (3, 6): ("shavuot 1", "Shavuot", 1),
        (3, 7): ("shavuot 2", "Shavuot", 2),

        (7, 1): ("rosh_hashanah 1", "Rosh Hashanah", 1),
        (7, 2): ("rosh_hashanah 2", "Rosh Hashanah", 2),

        (7, 10): ("yom_kippur", "Yom Kippur", 1),

        (7, 15): ("sukkot 1", "Sukkot", 1),
        (7, 16): ("sukkot 2", "Sukkot", 2),
        (7, 22): ("shemini_atzeret", "Shemini Atzeret", 1),
        (7, 23): ("simchat_torah", "Simchat Torah", 1),
    }

    key = (h.month, h.day)

    # ----------------------------
    # YOM TOV
    # ----------------------------
    if key in yom_tov_days:
        hk, name, day_index = yom_tov_days[key]

        return {
            "is_yom_tov": True,
            "is_erev_yom_tov": False,
            "holiday_key": hk,
            "holiday_name": name,
            "type": "yom_tov",
            "day_index": day_index
        }

    # ----------------------------
    # EREV YOM TOV
    # ----------------------------
    tomorrow = d + timedelta(days=1)

    tg = dates.GregorianDate(tomorrow.year, tomorrow.month, tomorrow.day)
    th = tg.to_heb()

    tomorrow_key = (th.month, th.day)

    if tomorrow_key in yom_tov_days:
        hk, name, day_index = yom_tov_days[tomorrow_key]

        return {
            "is_yom_tov": False,
            "is_erev_yom_tov": True,
            "holiday_key": hk,
            "holiday_name": f"Erev {name}",
            "type": "erev_yom_tov",
            "day_index": 0
        }

    # ----------------------------
    # NORMAL DAY
    # ----------------------------
    return {
        "is_yom_tov": False,
        "is_erev_yom_tov": False,
        "holiday_key": None,
        "holiday_name": None,
        "type": None,
        "day_index": None
    }
