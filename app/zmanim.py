from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
import json
import os

from pyluach import dates


# ----------------------------
# ZMANIM (REAL SUN BASED)
# ----------------------------
def calculate_zmanim(city, d):
    """
    Echte offline zmanim gebaseerd op zonpositie (Astral)
    """

    # config laden
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "config", "settings.json")

    with open(path, "r") as f:
        cfg = json.load(f)

    lat = cfg["latitude"]
    lon = cfg["longitude"]
    tz = pytz.timezone(cfg["timezone"])

    location = LocationInfo(
        name=city,
        region="",
        timezone=cfg["timezone"],
        latitude=lat,
        longitude=lon
    )

    # zondata
    s = sun(location.observer, date=d, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # halachische berekeningen
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)
    plag_hamincha = sunset - (1.25 * shaah_zmanit)

    alos = sunrise - timedelta(minutes=72)
    tzeis = sunset + timedelta(minutes=40)

    return {
        "alos": alos.strftime("%H:%M"),
        "chatzos": chatzos.strftime("%H:%M"),
        "plag_hamincha": plag_hamincha.strftime("%H:%M"),
        "shkia": sunset.strftime("%H:%M"),
        "tzeis": tzeis.strftime("%H:%M")
    }


# ----------------------------
# HOLIDAY LOGIC
# ----------------------------
def get_holiday_info(city, d):
    month_day = (d.month, d.day)

    holidays = {
        (5, 15): "Lag BaOmer",
        (1, 1): "Rosh Hashanah",
        (9, 10): "Yom Kippur"
    }

    if month_day in holidays:
        return {
            "is_yom_tov": True,
            "name": holidays[month_day]
        }

    return {
        "is_yom_tov": False,
        "name": None
    }


# ----------------------------
# HEBREW DATE (PYLUACH)
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
