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
def calculate_zmanim(config, d):
    """
    Safe production zmanim engine
    """

    # ----------------------------
    # VALIDATION (IMPORTANT)
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
    # SHAOT ZMANIOT
    # ----------------------------
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)
    plag = sunset - (1.25 * shaah_zmanit)

    # ----------------------------
    # SAFE CONFIG DEFAULTS
    # ----------------------------
    alos_cfg = config.get("alos", {"method": "fixed", "minutes": 72})
    tzeis_cfg = config.get("tzeis", {"method": "fixed", "minutes": 40})
    candle_min = config.get("candle_lighting", 18)

    # Alos
    if alos_cfg["method"] == "fixed":
        alos = sunrise - timedelta(minutes=alos_cfg["minutes"])
    else:
        raise ValueError("Unsupported alos method")

    # Tzeis
    if tzeis_cfg["method"] == "fixed":
        tzeis = sunset + timedelta(minutes=tzeis_cfg["minutes"])
    else:
        raise ValueError("Unsupported tzeis method")

    candle_lighting = sunset - timedelta(minutes=candle_min)

    # ----------------------------
    # OUTPUT (LOXONE FRIENDLY)
    # ----------------------------
    zmanim = {
        "alos": format_time(alos),
        "chatzos": format_time(chatzos),
        "plag_hamincha": format_time(plag),
        "shkia": format_time(sunset),
        "tzeis": format_time(tzeis),
        "candle_lighting": format_time(candle_lighting),

        # timestamps (belangrijk voor automation)
        "alos_ts": to_timestamp(alos),
        "plag_ts": to_timestamp(plag),
        "shkia_ts": to_timestamp(sunset),
        "tzeis_ts": to_timestamp(tzeis)
    }

    # ----------------------------
    # OVERRIDES (SAFE LAYER)
    # ----------------------------
    overrides = load_overrides(config["city"])
    zmanim = apply_overrides(zmanim, overrides, d)

    return zmanim


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
# HOLIDAYS (SIMPLE + STABLE)
# ----------------------------
def get_holiday_info(d):
    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    yom_tov_days = {
        (1, 1), (1, 2),
        (1, 10),
        (1, 15), (1, 16),
        (1, 22), (1, 23),
        (7, 15), (7, 16),
        (7, 21), (7, 22),
        (9, 6), (9, 7)
    }

    is_yom_tov = (h.month, h.day) in yom_tov_days

    return {
        "is_yom_tov": is_yom_tov,
        "name": "yom_tov" if is_yom_tov else None
    }
