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
    path = os.path.join(BASE_DIR, "data", f"{city}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def apply_overrides(zmanim, overrides, date):
    key = date.isoformat()
    if key in overrides:
        zmanim.update(overrides[key])
    return zmanim


def format_time(dt):
    return dt.strftime("%H:%M")


def to_timestamp(dt):
    return int(dt.timestamp())


# ----------------------------
# CORE ZMANIM
# ----------------------------
def calculate_zmanim(config, d):
    """
    Production-ready zmanim engine
    """

    tz = pytz.timezone(config["timezone"])

    location = LocationInfo(
        name=config["city"],
        region="",
        timezone=config["timezone"],
        latitude=config["latitude"],
        longitude=config["longitude"]
    )

    s = sun(location.observer, date=d, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # ----------------------------
    # SHAOT ZMANIOT (Gra)
    # ----------------------------
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)
    plag = sunset - (1.25 * shaah_zmanit)

    # ----------------------------
    # CONFIGURABLE TIMES
    # ----------------------------
    # Alos
    if config["alos"]["method"] == "fixed":
        alos = sunrise - timedelta(minutes=config["alos"]["minutes"])
    else:
        raise ValueError("Unsupported alos method")

    # Tzeis
    if config["tzeis"]["method"] == "fixed":
        tzeis = sunset + timedelta(minutes=config["tzeis"]["minutes"])
    else:
        raise ValueError("Unsupported tzeis method")

    # Candle lighting
    candle_lighting = sunset - timedelta(minutes=config["candle_lighting"])

    # ----------------------------
    # BUILD RESPONSE
    # ----------------------------
    zmanim = {
        "alos": format_time(alos),
        "chatzos": format_time(chatzos),
        "plag_hamincha": format_time(plag),
        "shkia": format_time(sunset),
        "tzeis": format_time(tzeis),
        "candle_lighting": format_time(candle_lighting),

        # timestamps (cruciaal voor Loxone)
        "alos_ts": to_timestamp(alos),
        "plag_ts": to_timestamp(plag),
        "shkia_ts": to_timestamp(sunset),
        "tzeis_ts": to_timestamp(tzeis)
    }

    # ----------------------------
    # OVERRIDES
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
# HOLIDAYS (HEBREW BASED)
# ----------------------------
def get_holiday_info(d):
    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    holidays = {
        (1, 1): "Rosh Hashanah",
        (1, 10): "Yom Kippur",
        (1, 15): "Sukkot",
        (1, 22): "Shemini Atzeret",
        (3, 25): "Chanukah",
        (7, 15): "Pesach",
        (2, 18): "Lag BaOmer"
    }

    name = holidays.get((h.month, h.day))

    return {
        "is_yom_tov": name is not None,
        "name": name
    }
