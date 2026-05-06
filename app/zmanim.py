from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
from pyluach import dates


# ----------------------------
# HELPERS
# ----------------------------
def format_time(dt):
    return dt.strftime("%H:%M")


def to_timestamp(dt):
    return int(dt.timestamp())


# ----------------------------
# SAFE CONFIG PARSER
# ----------------------------
def get_value(config, key, default):
    value = config.get(key, default)

    if isinstance(value, dict):
        return value.get("minutes", default)

    if isinstance(value, int) or isinstance(value, float):
        return value

    return default


# ----------------------------
# CORE ENGINE
# ----------------------------
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
    # CORE HALACHA TIMES
    # ----------------------------
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)
    plag = sunset - (1.25 * shaah_zmanit)

    # ----------------------------
    # SAFE CONFIG VALUES
    # ----------------------------
    alos_min = get_value(config, "alos", 72)
    tzeis_min = get_value(config, "tzeis", 40)
    candle_min = get_value(config, "candle_lighting", 18)

    # ----------------------------
    # TIMES
    # ----------------------------
    alos = sunrise - timedelta(minutes=alos_min)
    tzeis = sunset + timedelta(minutes=tzeis_min)
    candle = sunset - timedelta(minutes=candle_min)

    # ----------------------------
    # OUTPUT
    # ----------------------------
    return {
        "city": city,
        "date": d.isoformat(),

        # CORE
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
    }


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
# HOLIDAY ENGINE
# ----------------------------
def get_holiday_info(d):

    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    yom_tov_days = {
        (1, 15): ("pesach 1", "Pesach 1de", 1),
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
    tomorrow = d.fromordinal(d.toordinal() + 1)
    tg = dates.GregorianDate(tomorrow.year, tomorrow.month, tomorrow.day)
    th = tg.to_heb()

    if (th.month, th.day) in yom_tov_days:
        hk, name, _ = yom_tov_days[(th.month, th.day)]

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
